"""Disposable container lifecycle and command execution for benchmark runs."""

import shlex
import subprocess
import time
from types import TracebackType

import structlog

from installbench.config import settings
from installbench.models.benchmark_run import CommandExecution, RunPhase

logger = structlog.get_logger(__name__)
TIMEOUT_TERMINATION_GRACE_SECONDS = 5
HOST_TIMEOUT_BUFFER_SECONDS = 10
DIND_READY_TIMEOUT_SECONDS = 75
DIND_HEALTHCHECK_TIMEOUT_SECONDS = 5


class ContainerSandbox:
    """A fresh Docker or Podman container used for one benchmark run."""

    def __init__(self, base_image: str) -> None:
        self.base_image = base_image
        self.engine = settings.container_engine
        self.container_id: str | None = None

    def create(self) -> None:
        if self.container_id is not None:
            raise RuntimeError("Sandbox is already active.")

        run_command = [
            self.engine,
            "run",
            "--detach",
            "--label",
            "framework=installbench",
        ]
        if settings.sandbox_mode == "dind":
            run_command.extend(["--privileged", "--volume", "/var/lib/docker"])
        run_command.extend([self.base_image, "sleep", "infinity"])

        logger.info(
            "container_sandbox_starting",
            engine=self.engine,
            image=self.base_image,
            sandbox_mode=settings.sandbox_mode,
        )
        try:
            process = subprocess.run(
                run_command,
                capture_output=True,
                text=True,
                timeout=settings.command_timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Configured container engine is not installed: {self.engine}"
            ) from exc

        container_id = process.stdout.strip()
        if process.returncode != 0 or not container_id:
            detail = process.stderr.strip() or "Container engine returned no ID."
            raise RuntimeError(f"Failed to create {self.engine} sandbox: {detail}")

        self.container_id = container_id
        logger.info(
            "container_sandbox_started",
            engine=self.engine,
            container=container_id[:12],
        )

        if settings.sandbox_mode == "dind":
            try:
                self._wait_for_docker()
            except BaseException:
                self.destroy()
                raise

    def _wait_for_docker(self) -> None:
        """Wait until the private Docker daemon accepts commands."""

        if self.container_id is None:
            raise RuntimeError("Sandbox is not active.")

        deadline = time.monotonic() + DIND_READY_TIMEOUT_SECONDS
        last_error = "The Docker health check returned no diagnostic output."
        while time.monotonic() < deadline:
            try:
                process = subprocess.run(
                    [self.engine, "exec", self.container_id, "docker", "info"],
                    capture_output=True,
                    text=True,
                    timeout=DIND_HEALTHCHECK_TIMEOUT_SECONDS,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                last_error = "The Docker health check timed out."
            except OSError as exc:
                last_error = str(exc)
            else:
                if process.returncode == 0:
                    logger.info(
                        "dind_daemon_ready",
                        engine=self.engine,
                        container=self.container_id[:12],
                    )
                    return
                last_error = process.stderr.strip() or process.stdout.strip() or last_error
            time.sleep(1)

        try:
            logs_process = subprocess.run(
                [self.engine, "logs", self.container_id],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            container_logs = logs_process.stderr.strip() or logs_process.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            container_logs = ""

        detail = container_logs or last_error
        raise RuntimeError(
            f"Private Docker daemon was not ready after "
            f"{DIND_READY_TIMEOUT_SECONDS} seconds: {detail}"
        )

    def execute_command(
        self,
        command: str,
        *,
        phase: RunPhase,
        working_dir: str | None = None,
    ) -> CommandExecution:
        """Execute a non-interactive Bash command and preserve its evidence."""

        if self.container_id is None:
            raise RuntimeError("Sandbox is not active.")

        logger.debug(
            "command_execution_started",
            engine=self.engine,
            container=self.container_id[:12],
            phase=phase,
            command=command,
        )
        shell_command = "set -o pipefail\n"
        if working_dir:
            shell_command += f"cd {shlex.quote(working_dir)} || exit 125\n"
        shell_command += command

        timeout = settings.command_timeout_seconds
        host_timeout = timeout + TIMEOUT_TERMINATION_GRACE_SECONDS + HOST_TIMEOUT_BUFFER_SECONDS
        command_started_at = time.monotonic()
        try:
            process = subprocess.run(
                [
                    self.engine,
                    "exec",
                    self.container_id,
                    "/usr/bin/timeout",
                    "--signal=TERM",
                    f"--kill-after={TIMEOUT_TERMINATION_GRACE_SECONDS}s",
                    f"{timeout}s",
                    "/bin/bash",
                    "-lc",
                    shell_command,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=host_timeout,
                check=False,
            )
            elapsed_seconds = time.monotonic() - command_started_at
            timed_out = process.returncode in {124, 137} and elapsed_seconds >= timeout
            stderr = process.stderr
            if timed_out:
                message = f"Command timed out after {timeout} seconds."
                stderr = f"{stderr.rstrip()}\n{message}".lstrip()
                logger.warning(
                    "command_timed_out",
                    engine=self.engine,
                    command=command,
                    timeout=timeout,
                )
            return CommandExecution(
                phase=phase,
                command=command,
                exit_code=process.returncode,
                stdout=process.stdout,
                stderr=stderr,
                timed_out=timed_out,
            )
        except subprocess.TimeoutExpired as exc:
            logger.error(
                "command_timeout_enforcement_failed",
                engine=self.engine,
                command=command,
                configured_timeout=timeout,
                host_timeout=host_timeout,
            )
            raise RuntimeError(
                "The in-container timeout did not terminate the command; "
                "the sandbox can no longer be trusted."
            ) from exc
        except OSError as exc:
            logger.exception(
                "command_execution_failed",
                engine=self.engine,
                command=command,
            )
            return CommandExecution(
                phase=phase,
                command=command,
                exit_code=1,
                stderr=str(exc),
            )

    def destroy(self) -> None:
        container_id = self.container_id
        if container_id is None:
            return

        logger.info(
            "container_sandbox_stopping",
            engine=self.engine,
            container=container_id[:12],
        )
        try:
            remove_command = [self.engine, "rm", "--force"]
            if settings.sandbox_mode == "dind":
                remove_command.append("--volumes")
            remove_command.append(container_id)
            process = subprocess.run(
                remove_command,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if process.returncode != 0:
                logger.warning(
                    "container_sandbox_cleanup_failed",
                    engine=self.engine,
                    container=container_id[:12],
                    stderr=process.stderr.strip(),
                )
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.warning(
                "container_sandbox_cleanup_error",
                engine=self.engine,
                error=str(exc),
            )
        finally:
            self.container_id = None

    def __enter__(self) -> "ContainerSandbox":
        self.create()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.destroy()
