"""Orchestrate one benchmark run from task loading to result writing."""

import time
from collections.abc import Callable
from datetime import datetime

import structlog

from installbench.agents.agent_protocol import BenchmarkAgent
from installbench.benchmark_runner.repository_setup import prepare_repository
from installbench.config import settings
from installbench.models.benchmark_run import (
    BenchmarkRunResult,
    RunMetrics,
    RunStatus,
)
from installbench.models.execution import AgentRunStatus, CommandExecution
from installbench.models.installation import InstallationAgentResult, InstallationOutcome
from installbench.models.task import BenchmarkTask
from installbench.models.validation import ValidationAgentResult
from installbench.result_writer import JsonResultWriter, ResultWriter
from installbench.run_layout import allocate_run_layout
from installbench.sandbox.container_sandbox import ContainerSandbox
from installbench.sandbox.protocol import Sandbox
from installbench.task_loader import TaskLoader

logger = structlog.get_logger(__name__)
SandboxFactory = Callable[[str], Sandbox]


class BenchmarkRunner:
    """Execute a benchmark run and record its installation and validation evidence."""

    def __init__(
        self,
        installation_agent: BenchmarkAgent[InstallationAgentResult],
        validation_agent: BenchmarkAgent[ValidationAgentResult],
        *,
        task_loader: TaskLoader | None = None,
        result_writer: ResultWriter | None = None,
        sandbox_factory: SandboxFactory = ContainerSandbox,
    ) -> None:
        self.installation_agent = installation_agent
        self.validation_agent = validation_agent
        self.task_loader = task_loader or TaskLoader(settings.tasks_dir)
        self.result_writer = result_writer or JsonResultWriter(settings.results_dir)
        self.sandbox_factory = sandbox_factory

    @staticmethod
    def _format_documentation(task: BenchmarkTask) -> str:
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
        installation_duration: float,
        validation_duration: float,
        command_executions: list[CommandExecution],
    ) -> RunMetrics:
        return RunMetrics(
            duration_seconds=time.monotonic() - started_at,
            repository_setup_duration_seconds=repository_setup_duration,
            installation_duration_seconds=installation_duration,
            validation_duration_seconds=validation_duration,
            command_count=len(command_executions),
            repository_setup_command_count=sum(
                execution.phase == "repository_setup" for execution in command_executions
            ),
            installation_command_count=sum(
                execution.phase == "installation" for execution in command_executions
            ),
            validation_command_count=sum(
                execution.phase == "validation" for execution in command_executions
            ),
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
        installation_duration = 0.0
        validation_duration = 0.0
        command_executions: list[CommandExecution] = []
        installation_result: InstallationAgentResult | None = None
        validation_result: ValidationAgentResult | None = None
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
                    installation_result = self.installation_agent.run(
                        task=task,
                        sandbox=sandbox,
                        installation_guide=installation_guide,
                        run_id=run_id,
                        workspace_dir=run_layout.workspace_dir,
                    )
                    installation_duration = time.monotonic() - phase_started
                    command_executions.extend(installation_result.command_executions)
                    phase_started = time.monotonic()
                    validation_result = self.validation_agent.run(
                        task=task,
                        sandbox=sandbox,
                        installation_guide=installation_guide,
                        run_id=run_id,
                        workspace_dir=run_layout.workspace_dir,
                    )
                    validation_duration = time.monotonic() - phase_started
                    command_executions.extend(validation_result.command_executions)

                    if installation_result.status is not AgentRunStatus.COMPLETED:
                        run_status = RunStatus.INSTALLATION_AGENT_FAILED
                        error_message = installation_result.error_message or (
                            "The installation agent stopped with status: "
                            f"{installation_result.status.value}."
                        )
                    elif validation_result.status is not AgentRunStatus.COMPLETED:
                        run_status = RunStatus.VALIDATION_AGENT_FAILED
                        error_message = validation_result.error_message or (
                            "The validation agent stopped with status: "
                            f"{validation_result.status.value}."
                        )
                    else:
                        run_status = RunStatus.COMPLETED
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
            installation_agent_model=self.installation_agent.model_name,
            validation_agent_model=self.validation_agent.model_name,
            workspace_path=run_layout.workspace_dir.as_posix(),
            command_timeout_seconds=settings.command_timeout_seconds,
            max_installation_iterations=settings.max_installation_iterations,
            max_validation_iterations=settings.max_validation_iterations,
            started_at=started_at_timestamp,
            finished_at=finished_at_timestamp,
            run_status=run_status,
            installation_agent_status=(
                installation_result.status if installation_result else None
            ),
            installation_agent_outcome=(
                installation_result.outcome
                if installation_result
                else InstallationOutcome.UNKNOWN
            ),
            installation_report=(
                installation_result.report if installation_result else None
            ),
            validation_agent_status=(
                validation_result.status if validation_result else None
            ),
            validation_verdict=(
                validation_result.report.verdict
                if validation_result and validation_result.report
                else None
            ),
            validation_report=(validation_result.report if validation_result else None),
            metrics=self._build_metrics(
                started_at=started_at,
                repository_setup_duration=repository_setup_duration,
                installation_duration=installation_duration,
                validation_duration=validation_duration,
                command_executions=command_executions,
            ),
            command_executions=command_executions,
            installation_prompt=(installation_result.prompt if installation_result else ""),
            installation_agent_response=(
                installation_result.final_response if installation_result else ""
            ),
            installation_error_message=(
                installation_result.error_message if installation_result else None
            ),
            validation_prompt=(validation_result.prompt if validation_result else ""),
            validation_agent_response=(
                validation_result.final_response if validation_result else ""
            ),
            validation_error_message=(
                validation_result.error_message if validation_result else None
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
