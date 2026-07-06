"""Typing contract for agent integrations."""
from typing import Any, Protocol

from installbench.models.installation_task import InstallationTask
from installbench.sandbox.docker_manager import DockerManager


class AgentProtocol(Protocol):
    """An agent that can execute an installation task."""

    def invoke(
        self,
        task: InstallationTask,
        sandbox: DockerManager,
        prompt: str,
        experiment_id: str,
    ) -> dict[str, Any]:
        """Execute the task and return its commands, logs, and success state."""
        ...
