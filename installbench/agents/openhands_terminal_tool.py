"""Custom OpenHands terminal tool backed by a benchmark sandbox."""

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
from installbench.models.benchmark_run import CommandExecution, RunPhase
from installbench.sandbox.protocol import Sandbox


class InstallBenchTerminalAction(Action):
    """One non-interactive command executed with the benchmark timeout."""

    command: str = Field(description="Shell command to execute inside the container.")


class SandboxTerminalExecutor(ToolExecutor[InstallBenchTerminalAction, TerminalObservation]):
    """Execute OpenHands terminal actions through a benchmark sandbox."""

    def __init__(
        self,
        sandbox: Sandbox,
        command_executions: list[CommandExecution],
        working_dir: str,
        phase: RunPhase,
    ) -> None:
        self.sandbox = sandbox
        self.command_executions = command_executions
        self.working_dir = working_dir
        self.phase = phase

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

        command_execution = self.sandbox.execute_command(
            command,
            phase=self.phase,
            working_dir=self.working_dir,
        )
        self.command_executions.append(command_execution)
        output = "\n".join(
            part for part in (command_execution.stdout, command_execution.stderr) if part
        ).strip()

        return TerminalObservation.from_text(
            text=output,
            is_error=command_execution.exit_code != 0,
            command=command,
            exit_code=command_execution.exit_code,
            timeout=command_execution.timed_out,
            metadata=CmdOutputMetadata(
                exit_code=command_execution.exit_code,
                working_dir=self.working_dir,
            ),
        )


class InstallBenchTerminalTool(ToolDefinition[InstallBenchTerminalAction, TerminalObservation]):
    """OpenHands terminal tool backed by the active benchmark sandbox."""

    name = "terminal"

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Sequence[InstallBenchTerminalTool]:
        sandbox = kwargs["sandbox"]
        command_executions = kwargs["command_executions"]
        working_dir = kwargs["working_dir"]
        phase = kwargs["phase"]
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
                executor=SandboxTerminalExecutor(
                    sandbox=sandbox,
                    command_executions=command_executions,
                    working_dir=working_dir,
                    phase=phase,
                ),
            )
        ]
