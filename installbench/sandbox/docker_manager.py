"""
Manages isolated Docker environments for agent execution.
"""
import structlog
from typing import Optional
import docker  # Active real SDK integration

logger = structlog.get_logger(__name__)


class DockerManager:
    """Manages the lifecycle of real Docker containers used as sandboxes."""
    
    def __init__(self, base_image: str = "ubuntu:22.04") -> None:
        self.base_image = base_image
        self.container_id: Optional[str] = None
        self.container = None
        
        # Connect to the local Docker Desktop daemon running on Windows
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error("docker_connection_failed", error=str(e))
            raise RuntimeError(
                "Could not connect to Docker. Is Docker Desktop running?"
            ) from e
        
    def create_sandbox(self) -> None:
        """Creates and starts an isolated background Docker container."""
        logger.info("creating_docker_sandbox", image=self.base_image)
        
        try:
            # We run the container detached (detach=True) 
            # We give it an infinite dummy command ('sleep infinity') so it stays alive in the background
            self.container = self.client.containers.run(
                image=self.base_image,
                command="sleep infinity",
                detach=True,
                tty=True,
                labels={"framework": "installbench"}
            )
            self.container_id = self.container.id
            logger.info("sandbox_started_successfully", container_id=self.container_id[:12])
            
        except Exception as e:
            logger.error("sandbox_creation_failed", error=str(e))
            raise e

    def execute_command(self, command: str) -> tuple[int, str, str]:
        """
        Executes a live command inside the running sandbox container.
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.container:
            raise RuntimeError("Sandbox has not been created or is not active.")
        
        logger.debug("executing_command", container=self.container_id[:12], command=command)
        
        try:
            # Run through bash so pipes, redirects, and environment prefixes work.
            exec_result = self.container.exec_run(
                cmd=["/bin/bash", "-lc", command],
                demux=True,
            )
            
            exit_code = exec_result.exit_code
            
            # Unpack stdout and stderr (demux returns byte strings)
            stdout_bytes, stderr_bytes = exec_result.output
            stdout = stdout_bytes.decode("utf-8", errors="ignore") if stdout_bytes else ""
            stderr = stderr_bytes.decode("utf-8", errors="ignore") if stderr_bytes else ""
            
            return exit_code, stdout, stderr
            
        except Exception as e:
            logger.error("command_execution_error", command=command, error=str(e))
            return 1, "", str(e)

    def destroy_sandbox(self) -> None:
        """Stops and cleanly removes the container from your system."""
        if not self.container:
            return
            
        logger.info("destroying_docker_sandbox", container=self.container_id[:12])
        
        try:
            # Stop the execution loop and wipe out the container storage
            self.container.stop()
            self.container.remove()
        except Exception as e:
            logger.warning("sandbox_cleanup_warning", error=str(e))
        finally:
            self.container = None
            self.container_id = None

    def __enter__(self) -> "DockerManager":
        """Context manager support for guaranteed cleanup."""
        self.create_sandbox()
        return self
        
    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: type) -> None:
        self.destroy_sandbox()
