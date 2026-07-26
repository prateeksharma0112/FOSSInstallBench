"""Typing contract for disposable experiment sandboxes."""

from types import TracebackType
from typing import Protocol, Self

from installbench.models.experiment_result import CommandPhase, CommandResult


class Sandbox(Protocol):
    """A disposable environment capable of executing shell commands."""

    def execute_command(
        self,
        command: str,
        *,
        phase: CommandPhase,
        working_dir: str | None = None,
        timeout_seconds: int | None = None,
    ) -> CommandResult: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
