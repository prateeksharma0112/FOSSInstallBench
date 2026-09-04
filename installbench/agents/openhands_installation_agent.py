"""OpenHands SDK integration for installation benchmark runs."""

from __future__ import annotations

from pathlib import Path

import structlog
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.conversation.state import ConversationExecutionStatus
from openhands.sdk.tool.builtins.finish import FinishAction, FinishTool
from openhands.sdk.tool.registry import register_tool

from installbench.agents.openhands_terminal_tool import InstallBenchTerminalTool
from installbench.config import settings
from installbench.models.execution import AgentRunStatus, CommandExecution
from installbench.models.installation import (
    InstallationAgentResult,
    InstallationOutcome,
    InstallationReport,
)
from installbench.models.task import BenchmarkTask
from installbench.sandbox.protocol import Sandbox

logger = structlog.get_logger(__name__)


class OpenHandsInstallationAgent:
    """Runs installation tasks with the OpenHands Software Agent SDK."""

    def __init__(self) -> None:
        if not settings.installation_llm_model:
            raise ValueError("INSTALLATION_LLM_MODEL must be configured.")

        self.model_name = settings.installation_llm_model

        logger.info("initialized_openhands_installation_agent", model=self.model_name)

        if not settings.installation_llm_api_key:
            logger.warning(
                "missing_installation_llm_api_key",
                message="INSTALLATION_LLM_API_KEY is empty.",
            )

        self.llm = LLM(
            model=self.model_name,
            api_key=settings.installation_llm_api_key or None,
            base_url=settings.installation_llm_base_url,
        )

    def run(
        self,
        *,
        task: BenchmarkTask,
        sandbox: Sandbox,
        installation_guide: str,
        run_id: str,
        workspace_dir: Path,
    ) -> InstallationAgentResult:
        logger.info(
            "installation_agent_run_started",
            task_id=task.task_id,
            run_id=run_id,
        )

        persistence_dir = workspace_dir / ".openhands-installation"
        persistence_dir.mkdir(parents=True, exist_ok=True)

        prompt = self._build_prompt(task, installation_guide)

        command_executions: list[CommandExecution] = []
        terminal_tool = InstallBenchTerminalTool.create(
            sandbox=sandbox,
            command_executions=command_executions,
            working_dir=settings.repository_dir,
            phase="installation",
        )[0]
        register_tool("InstallBenchInstallationTerminalTool", terminal_tool)
        register_tool("InstallBenchInstallationFinishTool", FinishTool)

        conversation: Conversation | None = None
        try:
            agent = Agent(
                llm=self.llm,
                tools=[
                    Tool(name="InstallBenchInstallationTerminalTool"),
                    Tool(
                        name="InstallBenchInstallationFinishTool",
                        params={"response_schema": InstallationReport},
                    ),
                ],
                include_default_tools=["ThinkTool"],
            )
            conversation = Conversation(
                agent=agent,
                workspace=str(workspace_dir),
                persistence_dir=str(persistence_dir),
                max_iteration_per_run=settings.max_installation_iterations,
                visualizer=None,
            )
            conversation.send_message(prompt)
            conversation.run()
            execution_status = conversation.state.execution_status
            final_response = self._extract_final_response(conversation)
            installation_report = self._extract_installation_report(
                agent,
                conversation,
            )
            if execution_status != ConversationExecutionStatus.FINISHED:
                error_message = (
                    f"Installation agent stopped with status: {execution_status.value}"
                )
                return InstallationAgentResult(
                    status=AgentRunStatus.STOPPED,
                    command_executions=command_executions,
                    prompt=prompt,
                    final_response=final_response,
                    error_message=error_message,
                )
        except Exception as exc:
            error_message = self._safe_text(str(exc))
            logger.error(
                "installation_agent_run_error",
                task_id=task.task_id,
                error=error_message,
            )
            return InstallationAgentResult(
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
                    logger.warning("installation_conversation_close_failed", error=str(exc))

        return InstallationAgentResult(
            status=AgentRunStatus.COMPLETED,
            outcome=(
                installation_report.outcome
                if installation_report is not None
                else InstallationOutcome.UNKNOWN
            ),
            report=installation_report,
            command_executions=command_executions,
            prompt=prompt,
            final_response=final_response,
        )

    def _build_prompt(self, task: BenchmarkTask, installation_guide: str) -> str:
        template = settings.installation_prompt_path.read_text(encoding="utf-8")
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
        """Return the exact message supplied to the SDK's final Finish action."""

        try:
            events = list(conversation.state.events)
        except Exception as exc:
            logger.warning("installation_final_response_events_unavailable", error=str(exc))
            return ""

        for event in reversed(events):
            action = getattr(event, "action", None)
            if isinstance(action, FinishAction):
                return action.message
        return ""

    @staticmethod
    def _extract_installation_report(
        agent: Agent,
        conversation: Conversation,
    ) -> InstallationReport | None:
        """Read the validated report attached to the latest FinishTool call."""

        finish_tool = agent.tools_map["finish"]
        report = finish_tool.parse_last_response(conversation.state.events)
        if report is None:
            logger.warning("structured_installation_report_missing")
            return None
        return InstallationReport.model_validate(report)
