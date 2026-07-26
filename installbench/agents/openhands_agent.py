"""OpenHands SDK integration for installation experiments."""

from __future__ import annotations

import json
from pathlib import Path

import structlog
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.conversation.state import ConversationExecutionStatus
from openhands.sdk.tool.registry import register_tool

from installbench.agents.openhands_terminal_tool import InstallBenchTerminalTool
from installbench.config import settings
from installbench.models.experiment_result import AgentExecutionResult, CommandResult
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.protocol import Sandbox

logger = structlog.get_logger(__name__)
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "installation_prompt.txt"


class OpenHandsAgent:
    """Runs installation tasks with the OpenHands Software Agent SDK."""

    def __init__(self) -> None:
        if not settings.llm_model:
            raise ValueError("LLM_MODEL or INSTALLBENCH_LLM_MODEL must be configured.")

        self.model_name = settings.llm_model

        logger.info("initialized_openhands_agent", model=self.model_name)

        if not settings.llm_api_key:
            logger.warning("missing_llm_api_key", message="LLM_API_KEY is empty.")

        self.llm = LLM(
            model=self.model_name,
            api_key=settings.llm_api_key or None,
        )

    def run(
        self,
        *,
        task: InstallationTask,
        sandbox: Sandbox,
        installation_guide: str,
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

        prompt = self._build_prompt(task, installation_guide)

        command_log: list[CommandResult] = []
        terminal_tool = InstallBenchTerminalTool.create(
            sandbox=sandbox,
            command_log=command_log,
            working_dir=settings.repository_dir,
        )[0]
        register_tool("InstallBenchTerminalTool", terminal_tool)

        conversation: Conversation | None = None
        try:
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
            conversation.send_message(prompt)
            conversation.run()
            execution_status = conversation.state.execution_status
            if execution_status != ConversationExecutionStatus.FINISHED:
                error_message = f"Agent stopped with status: {execution_status.value}"
                return AgentExecutionResult(
                    finished=False,
                    commands=command_log,
                    logs=json.dumps(
                        {
                            "agent": "openhands",
                            "execution_status": execution_status.value,
                        },
                        indent=2,
                    ),
                    prompt=prompt,
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
                finished=False,
                commands=command_log,
                logs=json.dumps({"error": error_message}, indent=2),
                prompt=prompt,
                error_message=error_message,
            )
        finally:
            close = getattr(conversation, "close", None) if conversation else None
            if callable(close):
                try:
                    close()
                except Exception as exc:
                    logger.warning("conversation_close_failed", error=str(exc))

        return AgentExecutionResult(
            finished=True,
            commands=command_log,
            logs=json.dumps(
                {
                    "agent": "openhands",
                    "finished": True,
                    "execution_status": ConversationExecutionStatus.FINISHED.value,
                    "max_iterations": settings.max_agent_iterations,
                    "commands_logged": len(command_log),
                },
                indent=2,
            ),
            prompt=prompt,
        )

    def _build_prompt(self, task: InstallationTask, installation_guide: str) -> str:
        template = PROMPT_PATH.read_text(encoding="utf-8")
        return template.format(
            task_id=task.task_id,
            task_name=task.name,
            repository_url=task.repository_url,
            commit_sha=task.commit_sha.lower(),
            description=task.description,
            installation_guide=installation_guide,
        )

    @staticmethod
    def _safe_text(text: str) -> str:
        return text.encode("ascii", errors="replace").decode("ascii")
