"""
OpenHands SDK agent integration for InstallBench.
"""
from __future__ import annotations

import json
import os
from typing import Any

import structlog
from dotenv import load_dotenv
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.tool.registry import register_tool

from installbench.agents.openhands_docker_tool import InstallBenchTerminalTool
from installbench.config import settings
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.docker_manager import DockerManager

load_dotenv()
logger = structlog.get_logger(__name__)


class OpenHandsAgent:
    """Runs installation tasks with the OpenHands Software Agent SDK."""

    def __init__(self) -> None:
        self.model_name = os.getenv("LLM_MODEL")
        self.api_key = os.getenv("LLM_API_KEY")

        logger.info("initialized_openhands_agent", model=self.model_name)

        if not self.api_key:
            logger.warning("missing_llm_api_key", message="LLM_API_KEY is empty.")

        self.llm = LLM(
            model=self.model_name,
            api_key=self.api_key,
        )

    def invoke(
        self,
        task: InstallationTask,
        sandbox: DockerManager,
        prompt: str,
        experiment_id: str,
    ) -> dict[str, Any]:
        logger.info(
            "invoking_openhands_agent",
            task_id=task.task_id,
            experiment_id=experiment_id,
        )

        workspace_dir = settings.workspace_dir / task.task_id / experiment_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        persistence_dir = workspace_dir / ".openhands"
        persistence_dir.mkdir(parents=True, exist_ok=True)
        sandbox.execute_command("mkdir -p /workspace")

        command_log: list[dict[str, Any]] = []
        docker_terminal_tool = InstallBenchTerminalTool.create(
            sandbox=sandbox,
            command_log=command_log,
            working_dir="/workspace",
        )[0]
        register_tool("InstallBenchTerminalTool", docker_terminal_tool)

        agent = Agent(
            llm=self.llm,
            tools=[Tool(name="InstallBenchTerminalTool")],
        )

        conversation = Conversation(
            agent=agent,
            workspace=str(workspace_dir),
            persistence_dir=str(persistence_dir),
            visualizer=None,
        )

        try:
            conversation.send_message(self._build_prompt(task, prompt))
            conversation.run()
        except Exception as exc:
            error_message = self._safe_text(str(exc))
            logger.error(
                "openhands_execution_error",
                task_id=task.task_id,
                error=error_message,
            )
            return {
                "success": False,
                "commands": command_log,
                "stdout": self._format_stream(command_log, "stdout"),
                "stderr": self._format_stream(command_log, "stderr") or error_message,
                "logs": json.dumps({"error": error_message}, indent=2),
                "error_message": error_message,
            }
        finally:
            close = getattr(conversation, "close", None)
            if callable(close):
                close()

        validation_results = self._run_validation(task, sandbox)
        command_results = command_log + validation_results
        validation_ok = all(item["exit_code"] == 0 for item in validation_results)
        has_validation = bool(task.validation_commands)
        agent_attempt_ok = bool(command_log) and all(
            item["exit_code"] == 0 for item in command_log
        )
        success = validation_ok if has_validation else agent_attempt_ok

        return {
            "success": success,
            "commands": command_results,
            "stdout": self._format_stream(command_results, "stdout"),
            "stderr": self._format_stream(command_results, "stderr"),
            "logs": json.dumps(
                {
                    "agent": "openhands",
                    "validation_commands": task.validation_commands,
                    "validation_success": validation_ok,
                    "agent_attempt_success": agent_attempt_ok,
                    "commands_logged": len(command_log),
                },
                indent=2,
            ),
            "error_message": None,
        }

    def _build_prompt(self, task: InstallationTask, installation_guide: str) -> str:
        validation_text = "\n".join(f"- {cmd}" for cmd in task.validation_commands)
        return f"""
You are running an installation benchmark for InstallBench.

Task: {task.name}
Description: {task.description}

Environment:
- Fresh Ubuntu 22.04 Docker container.
- You are root inside the container.
- Do not use sudo.
- Avoid systemctl because systemd is usually unavailable in this container.
- Prefer non-interactive commands.
- Execute commands with the terminal tool.
- Treat the validation commands below as the exact final contract.
- Install so those commands pass from a fresh non-interactive shell.
- Do not rely on an activated shell session or virtual environment unless the
  validation command itself activates or references it.

Installation guide:
{installation_guide}

After installation, make sure these validation commands can pass:
{validation_text or "- No validation commands provided."}

Finish after the software is installed and validated.
"""

    def _run_validation(
        self,
        task: InstallationTask,
        sandbox: DockerManager,
    ) -> list[dict[str, Any]]:
        results = []
        for command in task.validation_commands:
            exit_code, stdout, stderr = sandbox.execute_command(
                command,
                working_dir="/workspace",
            )
            result = {
                "command": command,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "validation": True,
            }
            if self._is_infrastructure_error(stderr):
                result["error_type"] = "infrastructure"
            results.append(result)
        return results

    def _format_stream(self, results: list[dict[str, Any]], stream_name: str) -> str:
        parts = []
        for result in results:
            output = result.get(stream_name, "")
            if output:
                parts.append(f"$ {result['command']}\n{output}".rstrip())
        return "\n\n".join(parts)

    def _safe_text(self, text: str) -> str:
        return text.encode("ascii", errors="replace").decode("ascii")

    def _is_infrastructure_error(self, stderr: str) -> bool:
        return "RemoteDisconnected" in stderr or "Connection aborted" in stderr
