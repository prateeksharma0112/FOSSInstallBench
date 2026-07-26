"""Typing contract for installation agents."""

from typing import Protocol

from installbench.models.experiment_result import AgentExecutionResult
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.protocol import Sandbox


class AgentProtocol(Protocol):
    """An agent capable of attempting a documented installation."""

    model_name: str

    def run(
        self,
        *,
        task: InstallationTask,
        sandbox: Sandbox,
        installation_guide: str,
        experiment_id: str,
    ) -> AgentExecutionResult: ...
