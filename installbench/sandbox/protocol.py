"""Interface for disposable benchmark execution environments."""

from types import TracebackType
from typing import Protocol, Self

from installbench.models.agent_run import CommandExecution, RunPhase


class Sandbox(Protocol):
    """A disposable environment capable of executing shell commands."""

    def execute_command(
        self,
        command: str,
        *,
        phase: RunPhase,
        working_dir: str | None = None,
    ) -> CommandExecution: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
