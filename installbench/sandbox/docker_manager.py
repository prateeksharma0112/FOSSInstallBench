import shlex
import subprocess
from types import TracebackType

import docker
import structlog

logger = structlog.get_logger(__name__)


class DockerManager:
    def __init__(self, base_image: str = "ubuntu:22.04") -> None:
        self.base_image = base_image
        self.container_id: str | None = None
        self.container = None
        try:
            self.client = docker.from_env(timeout=300)
        except Exception as e:
            logger.error("docker_connection_failed", error=str(e))
            raise RuntimeError(
                "Could not connect to Podman. Is Podman Desktop running?"
            ) from e

    def create_sandbox(self) -> None:
        if self.container_id:
            raise RuntimeError("Sandbox is already active.")

        logger.info("creating_podman_sandbox", image=self.base_image)

        try:
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
                timeout=300,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Failed to create Podman sandbox: {result.stderr.strip()}"
                )

            self.container_id = result.stdout.strip()

            logger.info(
                "sandbox_started_successfully",
                container_id=self.container_id[:12],
            )
        except Exception as e:
            logger.error("sandbox_creation_failed", error=str(e))
            raise

    def execute_command(
        self,
        command: str,
        working_dir: str | None = None,
    ) -> tuple[int, str, str]:

        if not self.container_id:
            raise RuntimeError("Sandbox has not been created or is not active.")

        logger.debug(
            "executing_command", container=self.container_id[:12], command=command
        )

        try:
            shell_command = "set -eo pipefail\n"
            if working_dir:
                shell_command += f"cd {shlex.quote(working_dir)}\n"
            shell_command += command

            result = subprocess.run(
                [
                    "podman",
                    "exec",
                    self.container_id,
                    "/bin/bash",
                    "-lc",
                    shell_command,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=300,
            )

            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            logger.error("command_execution_error", command=command, error=str(e))
            return 1, "", str(e)

    def destroy_sandbox(self) -> None:
        
        container_id = self.container_id
        if not container_id:
            self.container = None
            return

        logger.info("destroying_podman_sandbox", container=self.container_id[:12])

        try:
            result = subprocess.run(
                ["podman", "rm", "-f", self.container_id],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                logger.warning(
                    "sandbox_cleanup_failed",
                    container=self.container_id[:12],
                    stderr=result.stderr,
                )
        except Exception as e:
            logger.warning("sandbox_cleanup_error", error=str(e))
        finally:
            self.container = None
            self.container_id = None

    def __enter__(self) -> "DockerManager":
        self.create_sandbox()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.destroy_sandbox()
