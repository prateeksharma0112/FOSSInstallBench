"""Lifecycle and command execution for a disposable Podman container."""

import shlex
import subprocess
import time
from types import TracebackType

import structlog

from installbench.config import settings
from installbench.models.experiment_result import CommandPhase, CommandResult

logger = structlog.get_logger(__name__)
TIMEOUT_TERMINATION_GRACE_SECONDS = 5
HOST_TIMEOUT_BUFFER_SECONDS = 10


class PodmanSandbox:
    """A fresh container used for exactly one experiment."""

    def __init__(self, base_image: str) -> None:
        self.base_image = base_image
        self.container_id: str | None = None

    def create(self) -> None:
        if self.container_id is not None:
            raise RuntimeError("Sandbox is already active.")

        logger.info("creating_podman_sandbox", image=self.base_image)
        result = subprocess.run(
            [
                "podman",
                "run",
                "--detach",
                "--label",
                "framework=installbench",
                self.base_image,
                "sleep",
                "infinity",
            ],
            capture_output=True,
            text=True,
            timeout=settings.command_timeout_seconds,
            check=False,
        )
        container_id = result.stdout.strip()
        if result.returncode != 0 or not container_id:
            detail = result.stderr.strip() or "Podman returned no container ID."
            raise RuntimeError(f"Failed to create Podman sandbox: {detail}")

        self.container_id = container_id
        logger.info("sandbox_started", container_id=container_id[:12])

    def execute_command(
        self,
        command: str,
        *,
        phase: CommandPhase,
        working_dir: str | None = None,
        timeout_seconds: int | None = None,
    ) -> CommandResult:
        """Execute a non-interactive Bash command and preserve all evidence."""

        if self.container_id is None:
            raise RuntimeError("Sandbox is not active.")

        logger.debug(
            "executing_command",
            container=self.container_id[:12],
            phase=phase,
            command=command,
        )
        shell_command = "set -o pipefail\n"
        if working_dir:
            shell_command += f"cd {shlex.quote(working_dir)} || exit 125\n"
        shell_command += command

        timeout = timeout_seconds or settings.command_timeout_seconds
        host_timeout = (
            timeout
            + TIMEOUT_TERMINATION_GRACE_SECONDS
            + HOST_TIMEOUT_BUFFER_SECONDS
        )
        command_started_at = time.monotonic()
        try:
            result = subprocess.run(
                [
                    "podman",
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
            timed_out = (
                result.returncode in {124, 137} and elapsed_seconds >= timeout
            )
            stderr = result.stderr
            if timed_out:
                message = f"Command timed out after {timeout} seconds."
                stderr = f"{stderr.rstrip()}\n{message}".lstrip()
                logger.warning(
                    "command_timed_out",
                    command=command,
                    timeout=timeout,
                )
            return CommandResult(
                phase=phase,
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=stderr,
                timed_out=timed_out,
            )
        except subprocess.TimeoutExpired as exc:
            logger.error(
                "command_timeout_enforcement_failed",
                command=command,
                configured_timeout=timeout,
                host_timeout=host_timeout,
            )
            raise RuntimeError(
                "The in-container timeout did not terminate the command; "
                "the sandbox can no longer be trusted."
            ) from exc
        except OSError as exc:
            logger.exception("command_execution_failed", command=command)
            return CommandResult(
                phase=phase,
                command=command,
                exit_code=1,
                stderr=str(exc),
            )

    def destroy(self) -> None:
        container_id = self.container_id
        if container_id is None:
            return

        logger.info("destroying_podman_sandbox", container=container_id[:12])
        try:
            result = subprocess.run(
                ["podman", "rm", "--force", container_id],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if result.returncode != 0:
                logger.warning(
                    "sandbox_cleanup_failed",
                    container=container_id[:12],
                    stderr=result.stderr.strip(),
                )
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.warning("sandbox_cleanup_error", error=str(exc))
        finally:
            self.container_id = None

    def __enter__(self) -> "PodmanSandbox":
        self.create()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.destroy()
