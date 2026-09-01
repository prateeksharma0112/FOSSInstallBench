"""Interface implemented by installation agents."""

from pathlib import Path
from typing import Protocol

from installbench.models.benchmark_run import AgentRunResult
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.protocol import Sandbox


class AgentInterface(Protocol):
    """An agent capable of attempting a documented software installation."""

    model_name: str

    def run(
        self,
        *,
        task: InstallationTask,
        sandbox: Sandbox,
        installation_guide: str,
        run_id: str,
        workspace_dir: Path,
    ) -> AgentRunResult: ...
