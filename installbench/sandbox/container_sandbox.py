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
        run_command.extend([self.base_image, "sleep", "infinity"])

        logger.info(
            "container_sandbox_starting",
            engine=self.engine,
            image=self.base_image,
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
            container_id=container_id[:12],
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
            process = subprocess.run(
                [self.engine, "rm", "--force", container_id],
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
