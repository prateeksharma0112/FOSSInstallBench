"""Orchestrate one installation experiment from input to stored result."""

import time
import uuid
from collections.abc import Callable

import structlog

from installbench.agents.protocol import AgentProtocol
from installbench.config import settings
from installbench.experiment.repository import prepare_repository
from installbench.models.experiment_result import (
    AgentExecutionResult,
    CommandResult,
    ExperimentMetrics,
    ExperimentResult,
    ExperimentStatus,
)
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.podman_sandbox import PodmanSandbox
from installbench.sandbox.protocol import Sandbox
from installbench.storage.json_storage import JsonStorage, ResultStorage
from installbench.tasks_loader.loader import TaskLoader

logger = structlog.get_logger(__name__)
SandboxFactory = Callable[[str], Sandbox]


class ExperimentRunner:
    """Run the framework setup, installation agent, and result recording."""

    def __init__(
        self,
        agent: AgentProtocol,
        *,
        task_loader: TaskLoader | None = None,
        storage: ResultStorage | None = None,
        sandbox_factory: SandboxFactory = PodmanSandbox,
    ) -> None:
        self.agent = agent
        self.task_loader = task_loader or TaskLoader(settings.tasks_dir)
        self.storage = storage or JsonStorage(settings.results_dir)
        self.sandbox_factory = sandbox_factory


    @staticmethod
    def _format_documentation(task: InstallationTask) -> str:
        sections = [
            f"## Guide: {name}\n\n{content.strip()}"
            for name, content in task.documentation_files.items()
        ]
        return "\n\n---\n\n".join(sections)

    @staticmethod
    def _first_failure(commands: list[CommandResult]) -> CommandResult | None:
        return next((command for command in commands if command.exit_code != 0), None)

    @staticmethod
    def _command_failure(stage: str, command: CommandResult) -> str:
        detail = command.stderr.strip() or command.stdout.strip() or "No output."
        return f"{stage} failed: {command.command}\n{detail}"

    @staticmethod
    def _build_metrics(
        *,
        started_at: float,
        setup_duration: float,
        agent_duration: float,
        commands: list[CommandResult],
    ) -> ExperimentMetrics:
        return ExperimentMetrics(
            duration_seconds=time.monotonic() - started_at,
            setup_duration_seconds=setup_duration,
            agent_duration_seconds=agent_duration,
            commands_executed_count=len(commands),
            setup_commands_count=sum(command.phase == "setup" for command in commands),
            agent_commands_count=sum(command.phase == "agent" for command in commands),
        )

    def run(self, task_id: str) -> ExperimentResult:
        started_at = time.monotonic()
        experiment_id = uuid.uuid4().hex
        task = self.task_loader.load(task_id)

        logger.info(
            "experiment_started",
            experiment_id=experiment_id,
            task_id=task.task_id,
            commit_sha=task.commit_sha,
        )

        setup_duration = 0.0
        agent_duration = 0.0
        commands: list[CommandResult] = []
        agent_result = AgentExecutionResult(finished=False)
        status = ExperimentStatus.SYSTEM_ERROR
        error_message: str | None = None

        try:
            with self.sandbox_factory(settings.default_container_image) as sandbox:
                phase_started = time.monotonic()
                setup_commands = prepare_repository(
                    task,
                    sandbox,
                    settings.repository_dir,
                )
                setup_duration = time.monotonic() - phase_started
                commands.extend(setup_commands)

                setup_failure = self._first_failure(setup_commands)
                if setup_failure is not None:
                    status = ExperimentStatus.SETUP_FAILED
                    error_message = self._command_failure(
                        "Repository setup",
                        setup_failure,
                    )
                else:
                    installation_guide = self._format_documentation(task)
                    phase_started = time.monotonic()
                    agent_result = self.agent.run(
                        task=task,
                        sandbox=sandbox,
                        installation_guide=installation_guide,
                        experiment_id=experiment_id,
                    )
                    agent_duration = time.monotonic() - phase_started
                    commands.extend(agent_result.commands)
                    error_message = agent_result.error_message
                    status = (
                        ExperimentStatus.AGENT_FINISHED
                        if agent_result.finished
                        else ExperimentStatus.AGENT_FAILED
                    )
                    if not agent_result.finished and error_message is None:
                        error_message = "The installation agent did not finish."
        except Exception as exc:
            logger.exception(
                "experiment_system_error",
                experiment_id=experiment_id,
                task_id=task.task_id,
            )
            status = ExperimentStatus.SYSTEM_ERROR
            error_message = str(exc)

        result = ExperimentResult(
            experiment_id=experiment_id,
            task_id=task.task_id,
            task_name=task.name,
            repository_url=task.repository_url,
            commit_sha=task.commit_sha.lower(),
            container_image=settings.default_container_image,
            agent_model=self.agent.model_name,
            status=status,
            metrics=self._build_metrics(
                started_at=started_at,
                setup_duration=setup_duration,
                agent_duration=agent_duration,
                commands=commands,
            ),
            commands=commands,
            agent_log=agent_result.logs,
            installation_prompt=agent_result.prompt,
            error_message=error_message,
        )
        self.storage.save(result)

        logger.info(
            "experiment_finished",
            experiment_id=experiment_id,
            status=status.value,
            commands_count=len(commands),
            duration_seconds=result.metrics.duration_seconds,
        )
        return result

