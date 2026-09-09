"""SDK-independent contract for benchmark agents."""

from pathlib import Path
from typing import Protocol, TypeVar

from installbench.models.task import BenchmarkTask
from installbench.models.validation import ValidationAgentResult
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
        agent_run_data_dir: Path,
    ) -> AgentResultT: ...


class ValidationAgent(Protocol):
    """Validator receiving factual context from the installation attempt."""

    model_name: str

    def run(
        self,
        *,
        task: BenchmarkTask,
        sandbox: Sandbox,
        installation_guide: str,
        installation_summary: str,
        run_id: str,
        agent_run_data_dir: Path,
    ) -> ValidationAgentResult: ...
