"""OpenHands terminal bridge for the active container sandbox."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from openhands.sdk import Action
from openhands.sdk.tool.tool import ToolAnnotations, ToolDefinition, ToolExecutor
from openhands.tools.terminal.definition import (
    CmdOutputMetadata,
    TerminalObservation,
)
from pydantic import Field

from installbench.config import settings
from installbench.models.experiment_result import CommandResult
from installbench.sandbox.protocol import Sandbox


class InstallBenchTerminalAction(Action):
    """One non-interactive command executed with the benchmark timeout."""

    command: str = Field(description="Shell command to execute inside the container.")


class ContainerTerminalExecutor(
    ToolExecutor[InstallBenchTerminalAction, TerminalObservation]
):
    """Execute agent terminal actions inside the repository checkout."""

    def __init__(
        self,
        sandbox: Sandbox,
        command_log: list[CommandResult],
        working_dir: str,
    ) -> None:
        self.sandbox = sandbox
        self.command_log = command_log
        self.working_dir = working_dir

    def __call__(
        self,
        action: InstallBenchTerminalAction,
        conversation: Any | None = None,
    ) -> TerminalObservation:
        command = action.command.strip()
        if not command:
            return TerminalObservation.from_text(
                text="",
                is_error=False,
                command=command,
                exit_code=0,
                metadata=CmdOutputMetadata(exit_code=0, working_dir=self.working_dir),
            )

        result = self.sandbox.execute_command(
            command,
            phase="agent",
            working_dir=self.working_dir,
        )
        self.command_log.append(result)
        output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()

        return TerminalObservation.from_text(
            text=output,
            is_error=result.exit_code != 0,
            command=command,
            exit_code=result.exit_code,
            timeout=result.timed_out,
            metadata=CmdOutputMetadata(
                exit_code=result.exit_code,
                working_dir=self.working_dir,
            ),
        )


class InstallBenchTerminalTool(
    ToolDefinition[InstallBenchTerminalAction, TerminalObservation]
):
    """OpenHands terminal tool backed by the active benchmark sandbox."""

    name = "terminal"

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Sequence[InstallBenchTerminalTool]:
        sandbox = kwargs["sandbox"]
        command_log = kwargs["command_log"]
        working_dir = kwargs["working_dir"]
        return [
            cls(
                description=(
                    "Execute one non-interactive shell command inside the source "
                    "repository. The shell runs as root in a fresh container. "
                    f"Every command has a fixed {settings.command_timeout_seconds}-second "
                    "timeout that cannot be overridden."
                ),
                action_type=InstallBenchTerminalAction,
                observation_type=TerminalObservation,
                annotations=ToolAnnotations(
                    title="terminal",
                    readOnlyHint=False,
                    destructiveHint=True,
                    idempotentHint=False,
                    openWorldHint=True,
                ),
                executor=ContainerTerminalExecutor(
                    sandbox=sandbox,
                    command_log=command_log,
                    working_dir=working_dir,
                ),
            )
        ]
