"""SDK-independent contract for benchmark agents."""

from pathlib import Path
from typing import Protocol, TypeVar

from installbench.models.task import BenchmarkTask
from installbench.sandbox.protocol import Sandbox

AgentResultT = TypeVar("AgentResultT", covariant=True)


class BenchmarkAgent(Protocol[AgentResultT]):
    """An agent operating on a benchmark task and its sandbox."""

    model_name: str

    def run(
        self,
        *,
        task: BenchmarkTask,
        sandbox: Sandbox,
        installation_guide: str,
        run_id: str,
        workspace_dir: Path,
    ) -> AgentResultT: ...
