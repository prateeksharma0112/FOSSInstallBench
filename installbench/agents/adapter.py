"""Typing contract for agent integrations."""

from typing import Protocol

from installbench.models.experiment_result import AgentExecutionResult
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.podman_sandbox import PodmanSandbox


class AgentProtocol(Protocol):
    """An agent that can execute an installation task."""

    model_name: str

    def invoke(
        self,
        task: InstallationTask,
        sandbox: PodmanSandbox,
        prompt: str,
        experiment_id: str,
    ) -> AgentExecutionResult:
        """Install the task and return command history and completion state."""
        ...
