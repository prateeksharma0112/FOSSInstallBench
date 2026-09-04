"""OpenHands SDK integration for independent installation validation."""

from __future__ import annotations

from pathlib import Path

import structlog
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.conversation.state import ConversationExecutionStatus
from openhands.sdk.tool.builtins.finish import FinishAction, FinishTool
from openhands.sdk.tool.registry import register_tool

from installbench.agents.openhands_terminal_tool import InstallBenchTerminalTool
from installbench.config import settings
from installbench.models.benchmark_run import AgentRunStatus, CommandExecution
from installbench.models.installation_task import InstallationTask
from installbench.models.validation import ValidationAgentResult, ValidationReport
from installbench.sandbox.protocol import Sandbox

logger = structlog.get_logger(__name__)


class OpenHandsValidationAgent:
    """Independently validate an installation in its existing sandbox."""

    def __init__(self) -> None:
        if not settings.validation_llm_model:
            raise ValueError("VALIDATION_LLM_MODEL must be configured.")

        self.model_name = settings.validation_llm_model

        logger.info("initialized_openhands_validation_agent", model=self.model_name)

        if not settings.validation_llm_api_key:
            logger.warning(
                "missing_validation_llm_api_key",
                message="VALIDATION_LLM_API_KEY is empty.",
            )

        self.llm = LLM(
            model=self.model_name,
            api_key=settings.validation_llm_api_key or None,
            base_url=settings.validation_llm_base_url,
        )

    def run(
        self,
        *,
        task: InstallationTask,
        sandbox: Sandbox,
        installation_guide: str,
        run_id: str,
        workspace_dir: Path,
    ) -> ValidationAgentResult:
        logger.info(
            "validation_agent_run_started",
            task_id=task.task_id,
            run_id=run_id,
        )

        persistence_dir = workspace_dir / ".openhands-validation"
        persistence_dir.mkdir(parents=True, exist_ok=True)
        prompt = self._build_prompt(task, installation_guide)

        command_executions: list[CommandExecution] = []
        terminal_tool = InstallBenchTerminalTool.create(
            sandbox=sandbox,
            command_executions=command_executions,
            working_dir=settings.repository_dir,
            phase="validation",
        )[0]
        register_tool("InstallBenchValidationTerminalTool", terminal_tool)
        register_tool("InstallBenchValidationFinishTool", FinishTool)

        conversation: Conversation | None = None
        try:
            agent = Agent(
                llm=self.llm,
                tools=[
                    Tool(name="InstallBenchValidationTerminalTool"),
                    Tool(
                        name="InstallBenchValidationFinishTool",
                        params={"response_schema": ValidationReport},
                    ),
                ],
                include_default_tools=["ThinkTool"],
            )
            conversation = Conversation(
                agent=agent,
                workspace=str(workspace_dir),
                persistence_dir=str(persistence_dir),
                max_iteration_per_run=settings.max_validation_iterations,
                visualizer=None,
            )
            conversation.send_message(prompt)
            conversation.run()
            execution_status = conversation.state.execution_status
            final_response = self._extract_final_response(conversation)
            validation_report = self._extract_validation_report(agent, conversation)

            if execution_status != ConversationExecutionStatus.FINISHED:
                error_message = f"Validation agent stopped with status: {execution_status.value}"
                return ValidationAgentResult(
                    status=AgentRunStatus.STOPPED,
                    command_executions=command_executions,
                    prompt=prompt,
                    final_response=final_response,
                    error_message=error_message,
                )
        except Exception as exc:
            error_message = self._safe_text(str(exc))
            logger.error(
                "validation_agent_run_error",
                task_id=task.task_id,
                error=error_message,
            )
            return ValidationAgentResult(
                status=AgentRunStatus.ERROR,
                command_executions=command_executions,
                prompt=prompt,
                final_response=(
                    self._extract_final_response(conversation) if conversation else ""
                ),
                error_message=error_message,
            )
        finally:
            close = getattr(conversation, "close", None)
            if callable(close):
                try:
                    close()
                except Exception as exc:
                    logger.warning("validation_conversation_close_failed", error=str(exc))

        return ValidationAgentResult(
            status=AgentRunStatus.COMPLETED,
            report=validation_report,
            command_executions=command_executions,
            prompt=prompt,
            final_response=final_response,
        )

    @staticmethod
    def _build_prompt(task: InstallationTask, installation_guide: str) -> str:
        template = settings.validation_prompt_path.read_text(encoding="utf-8")
        return template.format(
            task_name=task.name,
            description=task.description,
            installation_guide=installation_guide,
        )

    @staticmethod
    def _safe_text(text: str) -> str:
        return text.encode("ascii", errors="replace").decode("ascii")

    @staticmethod
    def _extract_final_response(conversation: Conversation) -> str:
        try:
            events = list(conversation.state.events)
        except Exception as exc:
            logger.warning("validation_final_response_events_unavailable", error=str(exc))
            return ""

        for event in reversed(events):
            action = getattr(event, "action", None)
            if isinstance(action, FinishAction):
                return action.message
        return ""

    @staticmethod
    def _extract_validation_report(
        agent: Agent,
        conversation: Conversation,
    ) -> ValidationReport | None:
        finish_tool = agent.tools_map["finish"]
        report = finish_tool.parse_last_response(conversation.state.events)
        if report is None:
            logger.warning("structured_validation_report_missing")
            return None
        return ValidationReport.model_validate(report)
