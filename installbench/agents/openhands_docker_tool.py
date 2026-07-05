"""
OpenHands tool bridge for the InstallBench Docker sandbox.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from openhands.sdk.tool.tool import ToolAnnotations, ToolDefinition, ToolExecutor
from openhands.tools.terminal.definition import (
    CmdOutputMetadata,
    TerminalAction,
    TerminalObservation,
)

from installbench.sandbox.docker_manager import DockerManager


class DockerTerminalExecutor(ToolExecutor[TerminalAction, TerminalObservation]):
    """Executes OpenHands terminal actions inside an InstallBench Docker container."""

    def __init__(
        self,
        sandbox: DockerManager,
        command_log: list[dict[str, Any]],
        working_dir: str = "/workspace",
    ) -> None:
        self.sandbox = sandbox
        self.command_log = command_log
        self.working_dir = working_dir

    def __call__(
        self,
        action: TerminalAction,
        conversation: Any | None = None,
    ) -> TerminalObservation:
        if action.is_input:
            return TerminalObservation.from_text(
                text="Interactive terminal input is not supported in InstallBench Docker mode.",
                is_error=True,
                command=action.command,
                exit_code=1,
                metadata=CmdOutputMetadata(exit_code=1, working_dir=self.working_dir),
            )

        command = action.command.strip()
        if not command:
            return TerminalObservation.from_text(
                text="",
                is_error=False,
                command=command,
                exit_code=0,
                metadata=CmdOutputMetadata(exit_code=0, working_dir=self.working_dir),
            )

        exit_code, stdout, stderr = self.sandbox.execute_command(
            command,
            working_dir=self.working_dir,
        )
        output = stdout
        if stderr:
            output = f"{stdout}\n{stderr}".strip()

        command_result = {
            "command": command,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
        }
        if _is_infrastructure_error(stderr):
            command_result["error_type"] = "infrastructure"

        self.command_log.append(command_result)

        return TerminalObservation.from_text(
            text=output,
            is_error=exit_code != 0,
            command=command,
            exit_code=exit_code,
            metadata=CmdOutputMetadata(exit_code=exit_code, working_dir=self.working_dir),
        )


class InstallBenchTerminalTool(ToolDefinition[TerminalAction, TerminalObservation]):
    """OpenHands terminal tool backed by the active InstallBench Docker sandbox."""

    name = "terminal"

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Sequence["InstallBenchTerminalTool"]:
        sandbox = kwargs["sandbox"]
        command_log = kwargs["command_log"]
        working_dir = kwargs.get("working_dir", "/workspace")

        return [
            cls(
                description=(
                    "Execute one shell command inside the fresh Ubuntu Docker "
                    "container used for this installation benchmark. The shell "
                    "runs as root. Do not use sudo. Avoid systemctl because "
                    "systemd is usually unavailable in this container."
                ),
                action_type=TerminalAction,
                observation_type=TerminalObservation,
                annotations=ToolAnnotations(
                    title="terminal",
                    readOnlyHint=False,
                    destructiveHint=True,
                    idempotentHint=False,
                    openWorldHint=True,
                ),
                executor=DockerTerminalExecutor(
                    sandbox=sandbox,
                    command_log=command_log,
                    working_dir=working_dir,
                ),
            )
        ]


def _is_infrastructure_error(stderr: str) -> bool:
    return "RemoteDisconnected" in stderr or "Connection aborted" in stderr
