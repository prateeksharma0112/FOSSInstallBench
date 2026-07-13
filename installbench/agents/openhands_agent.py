"""
OpenHands SDK agent integration for InstallBench.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import structlog
from dotenv import load_dotenv
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.conversation.state import ConversationExecutionStatus
from openhands.sdk.tool.registry import register_tool

from installbench.agents.openhands_terminal_tool import InstallBenchTerminalTool
from installbench.config import settings
from installbench.models.experiment_result import AgentExecutionResult, CommandResult
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.podman_sandbox import PodmanSandbox

load_dotenv()
logger = structlog.get_logger(__name__)
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "installation_prompt.txt"


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
        sandbox: PodmanSandbox,
        prompt: str,
        experiment_id: str,
    ) -> AgentExecutionResult:
        logger.info(
            "invoking_openhands_agent",
            task_id=task.task_id,
            experiment_id=experiment_id,
        )

        workspace_dir = settings.workspace_dir / task.task_id / experiment_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        persistence_dir = workspace_dir / ".openhands"
        persistence_dir.mkdir(parents=True, exist_ok=True)

        command_log: list[CommandResult] = []
        terminal_tool = InstallBenchTerminalTool.create(
            sandbox=sandbox,
            command_log=command_log,
            working_dir=settings.repository_dir,
        )[0]
        register_tool("InstallBenchTerminalTool", terminal_tool)

        agent = Agent(
            llm=self.llm,
            tools=[Tool(name="InstallBenchTerminalTool")],
        )

        conversation = Conversation(
            agent=agent,
            workspace=str(workspace_dir),
            persistence_dir=str(persistence_dir),
            max_iteration_per_run=settings.max_agent_iterations,
            visualizer=None,
        )

        try:
            conversation.send_message(self._build_prompt(task, prompt))
            conversation.run()
            execution_status = conversation.state.execution_status
            if execution_status != ConversationExecutionStatus.FINISHED:
                error_message = f"Agent stopped with status: {execution_status.value}"
                return AgentExecutionResult(
                    completed=False,
                    commands=command_log,
                    logs=json.dumps(
                        {
                            "agent": "openhands",
                            "execution_status": execution_status.value,
                        },
                        indent=2,
                    ),
                    error_message=error_message,
                )
        except Exception as exc:
            error_message = self._safe_text(str(exc))
            logger.error(
                "openhands_execution_error",
                task_id=task.task_id,
                error=error_message,
            )
            return AgentExecutionResult(
                completed=False,
                commands=command_log,
                logs=json.dumps({"error": error_message}, indent=2),
                error_message=error_message,
            )
        finally:
            close = getattr(conversation, "close", None)
            if callable(close):
                try:
                    close()
                except Exception as exc:
                    logger.warning("conversation_close_failed", error=str(exc))

        return AgentExecutionResult(
            completed=True,
            commands=command_log,
            logs=json.dumps(
                {
                    "agent": "openhands",
                    "completed": True,
                    "execution_status": ConversationExecutionStatus.FINISHED.value,
                    "max_iterations": settings.max_agent_iterations,
                    "commands_logged": len(command_log),
                },
                indent=2,
            ),
        )

    def _build_prompt(self, task: InstallationTask, installation_guide: str) -> str:
        template = PROMPT_PATH.read_text(encoding="utf-8")
        return template.format(
            task_name=task.name,
            description=task.description,
            container_image=settings.default_container_image,
            repository_dir=settings.repository_dir,
            installation_guide=installation_guide,
        )

    def _safe_text(self, text: str) -> str:
        return text.encode("ascii", errors="replace").decode("ascii")
