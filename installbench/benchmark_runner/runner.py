"""Orchestrate one benchmark run from task loading to result writing."""

import time
from collections.abc import Callable
from datetime import datetime

import structlog

from installbench.agents.agent_interface import AgentInterface
from installbench.benchmark_runner.repository_setup import prepare_repository
from installbench.config import settings
from installbench.models.benchmark_run import (
    AgentRunResult,
    AgentRunStatus,
    BenchmarkRunResult,
    CommandExecution,
    InstallationOutcome,
    RunMetrics,
    RunStatus,
)
from installbench.models.installation_task import InstallationTask
from installbench.result_writer import JsonResultWriter, ResultWriter
from installbench.run_layout import allocate_run_layout
from installbench.sandbox.container_sandbox import ContainerSandbox
from installbench.sandbox.protocol import Sandbox
from installbench.task_loader import TaskLoader

logger = structlog.get_logger(__name__)
SandboxFactory = Callable[[str], Sandbox]


class BenchmarkRunner:
    """Execute an installation benchmark run and record its evidence."""

    def __init__(
        self,
        agent: AgentInterface,
        *,
        task_loader: TaskLoader | None = None,
        result_writer: ResultWriter | None = None,
        sandbox_factory: SandboxFactory = ContainerSandbox,
    ) -> None:
        self.agent = agent
        self.task_loader = task_loader or TaskLoader(settings.tasks_dir)
        self.result_writer = result_writer or JsonResultWriter(settings.results_dir)
        self.sandbox_factory = sandbox_factory

    @staticmethod
    def _format_documentation(task: InstallationTask) -> str:
        sections = [
            f"## Guide: {name}\n\n{content.strip()}"
            for name, content in task.documentation_files.items()
        ]
        return "\n\n---\n\n".join(sections)

    @staticmethod
    def _first_failure(
        command_executions: list[CommandExecution],
    ) -> CommandExecution | None:
        return next(
            (execution for execution in command_executions if execution.exit_code != 0),
            None,
        )

    @staticmethod
    def _command_failure(stage: str, execution: CommandExecution) -> str:
        detail = execution.stderr.strip() or execution.stdout.strip() or "No output."
        return f"{stage} failed: {execution.command}\n{detail}"

    @staticmethod
    def _build_metrics(
        *,
        started_at: float,
        repository_setup_duration: float,
        agent_run_duration: float,
        command_executions: list[CommandExecution],
    ) -> RunMetrics:
        return RunMetrics(
            duration_seconds=time.monotonic() - started_at,
            repository_setup_duration_seconds=repository_setup_duration,
            agent_run_duration_seconds=agent_run_duration,
            command_count=len(command_executions),
            repository_setup_command_count=sum(
                execution.phase == "repository_setup" for execution in command_executions
            ),
            agent_command_count=sum(execution.phase == "agent" for execution in command_executions),
        )

    def run(self, task_id: str) -> BenchmarkRunResult:
        started_at_timestamp = datetime.now().astimezone()
        started_at = time.monotonic()
        task = self.task_loader.load(task_id)
        run_layout = allocate_run_layout(
            experiment_id=settings.experiment_id,
            task_id=task.task_id,
            results_dir=settings.results_dir,
            workspace_dir=settings.workspace_dir,
        )
        run_id = run_layout.run_id

        logger.info(
            "benchmark_run_started",
            run_id=run_id,
            task_id=task.task_id,
            commit_sha=task.commit_sha,
        )

        repository_setup_duration = 0.0
        agent_run_duration = 0.0
        command_executions: list[CommandExecution] = []
        agent_run_result: AgentRunResult | None = None
        run_status = RunStatus.SYSTEM_ERROR
        error_message: str | None = None

        try:
            with self.sandbox_factory(settings.default_container_image) as sandbox:
                phase_started = time.monotonic()
                setup_executions = prepare_repository(
                    task,
                    sandbox,
                    settings.repository_dir,
                )
                repository_setup_duration = time.monotonic() - phase_started
                command_executions.extend(setup_executions)

                setup_failure = self._first_failure(setup_executions)
                if setup_failure is not None:
                    run_status = RunStatus.REPOSITORY_SETUP_FAILED
                    error_message = self._command_failure(
                        "Repository setup",
                        setup_failure,
                    )
                else:
                    installation_guide = self._format_documentation(task)
                    phase_started = time.monotonic()
                    agent_run_result = self.agent.run(
                        task=task,
                        sandbox=sandbox,
                        installation_guide=installation_guide,
                        run_id=run_id,
                        workspace_dir=run_layout.workspace_dir,
                    )
                    agent_run_duration = time.monotonic() - phase_started
                    command_executions.extend(agent_run_result.command_executions)
                    error_message = agent_run_result.error_message
                    run_status = (
                        RunStatus.COMPLETED
                        if agent_run_result.agent_run_status is AgentRunStatus.COMPLETED
                        else RunStatus.AGENT_RUN_FAILED
                    )
                    if run_status is RunStatus.AGENT_RUN_FAILED and error_message is None:
                        error_message = (
                            "The installation agent stopped with status: "
                            f"{agent_run_result.agent_run_status.value}."
                        )
        except Exception as exc:
            logger.exception(
                "benchmark_run_system_error",
                run_id=run_id,
                task_id=task.task_id,
            )
            run_status = RunStatus.SYSTEM_ERROR
            error_message = str(exc)

        finished_at_timestamp = datetime.now().astimezone()
        run_result = BenchmarkRunResult(
            run_id=run_id,
            experiment_id=run_layout.experiment_id,
            run_number=run_layout.run_number,
            dataset_id=task.dataset_id,
            task_id=task.task_id,
            task_name=task.name,
            repository_url=task.repository_url,
            commit_sha=task.commit_sha.lower(),
            container_image=settings.default_container_image,
            container_engine=settings.container_engine,
            sandbox_mode=settings.sandbox_mode,
            agent_model=self.agent.model_name,
            workspace_path=run_layout.workspace_dir.as_posix(),
            command_timeout_seconds=settings.command_timeout_seconds,
            max_agent_iterations=settings.max_agent_iterations,
            started_at=started_at_timestamp,
            finished_at=finished_at_timestamp,
            run_status=run_status,
            agent_run_status=(agent_run_result.agent_run_status if agent_run_result else None),
            installation_outcome=(
                agent_run_result.installation_outcome
                if agent_run_result
                else InstallationOutcome.UNKNOWN
            ),
            installation_report=(
                agent_run_result.installation_report if agent_run_result else None
            ),
            metrics=self._build_metrics(
                started_at=started_at,
                repository_setup_duration=repository_setup_duration,
                agent_run_duration=agent_run_duration,
                command_executions=command_executions,
            ),
            command_executions=command_executions,
            installation_prompt=(agent_run_result.installation_prompt if agent_run_result else ""),
            agent_final_response=(
                agent_run_result.agent_final_response if agent_run_result else ""
            ),
            error_message=error_message,
        )
        self.result_writer.write(run_result)

        logger.info(
            "benchmark_run_finished",
            run_id=run_id,
            run_status=run_status.value,
            command_count=len(command_executions),
            duration_seconds=run_result.metrics.duration_seconds,
        )
        return run_result
