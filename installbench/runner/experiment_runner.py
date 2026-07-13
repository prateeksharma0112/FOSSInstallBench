import shlex
import time
import uuid
from collections.abc import Callable

import structlog

from installbench.agents.adapter import AgentProtocol
from installbench.config import settings
from installbench.datasets.loader import DatasetLoader
from installbench.models.experiment_result import (
    AgentExecutionResult,
    CommandResult,
    ExperimentMetrics,
    ExperimentResult,
)
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.podman_sandbox import PodmanSandbox
from installbench.storage.json_storage import JsonStorage

logger = structlog.get_logger(__name__)
SandboxFactory = Callable[[str], PodmanSandbox]


class ExperimentRunner:
    """Run deterministic preparation and validation around an autonomous agent."""

    def __init__(
        self,
        agent: AgentProtocol,
        *,
        dataset_loader: DatasetLoader | None = None,
        storage: JsonStorage | None = None,
        sandbox_factory: SandboxFactory = PodmanSandbox,
    ) -> None:
        self.agent = agent
        self.dataset_loader = dataset_loader or DatasetLoader(settings.tasks_dir)
        self.storage = storage or JsonStorage(settings.results_dir)
        self.sandbox_factory = sandbox_factory

    def run(self, task_id: str) -> ExperimentResult:
        experiment_id = uuid.uuid4().hex
        task = self.dataset_loader.load_task(task_id)
        logger.info(
            "starting_experiment",
            experiment_id=experiment_id,
            task_id=task_id,
            commit_sha=task.commit_sha,
        )

        started_at = time.monotonic()
        setup_duration = 0.0
        agent_duration = 0.0
        validation_duration = 0.0
        commands: list[CommandResult] = []
        agent_result = AgentExecutionResult(completed=False)
        error_message: str | None = None

        try:
            with self.sandbox_factory(settings.default_container_image) as sandbox:
                phase_started = time.monotonic()
                setup_commands = self._prepare_repository(task, sandbox)
                setup_duration = time.monotonic() - phase_started
                commands.extend(setup_commands)

                setup_failure = self._first_failure(setup_commands)
                if setup_failure is not None:
                    error_message = self._failure_message(
                        "Repository setup", setup_failure
                    )
                else:
                    guide = self._format_documentation(task)
                    phase_started = time.monotonic()
                    agent_result = self.agent.invoke(
                        task,
                        sandbox,
                        guide,
                        experiment_id,
                    )
                    agent_duration = time.monotonic() - phase_started
                    commands.extend(agent_result.commands)
                    error_message = agent_result.error_message

                    # Validation is intentionally disabled while the installation
                    # workflow is being developed. Re-enable this block once the
                    # validation strategy has been defined.
                    # if agent_result.completed:
                    #     phase_started = time.monotonic()
                    #     validation_commands = self._run_validation(task, sandbox)
                    #     validation_duration = time.monotonic() - phase_started
                    #     commands.extend(validation_commands)
                    #     validation_failure = self._first_failure(validation_commands)
                    #     if validation_failure is not None:
                    #         error_message = self._failure_message(
                    #             "Validation", validation_failure
                    #         )
        except Exception as exc:
            logger.exception("experiment_execution_failed", task_id=task_id)
            error_message = str(exc)

        setup_ok = self._phase_passed(commands, "setup")
        # validation_ok = self._phase_passed(commands, "validation")
        success = setup_ok and agent_result.completed
        if not success and error_message is None:
            error_message = "Agent did not complete the installation task."

        duration = time.monotonic() - started_at
        metrics = ExperimentMetrics(
            duration_seconds=duration,
            setup_duration_seconds=setup_duration,
            agent_duration_seconds=agent_duration,
            validation_duration_seconds=validation_duration,
            success=success,
            commands_executed_count=len(commands),
            setup_commands_count=self._phase_count(commands, "setup"),
            agent_commands_count=self._phase_count(commands, "agent"),
            validation_commands_count=self._phase_count(commands, "validation"),
        )
        result = ExperimentResult(
            experiment_id=experiment_id,
            task_id=task.task_id,
            task_name=task.name,
            repository_url=task.repository_url,
            commit_sha=task.commit_sha.lower(),
            container_image=settings.default_container_image,
            agent_model=self.agent.model_name,
            metrics=metrics,
            commands=commands,
            stdout=self._format_stream(commands, "stdout"),
            stderr=self._format_stream(commands, "stderr"),
            agent_log=agent_result.logs,
            error_message=error_message,
        )
        self.storage.store(result)
        logger.info(
            "experiment_completed",
            experiment_id=experiment_id,
            success=success,
            commands_count=len(commands),
            duration_seconds=duration,
        )
        return result

    def _prepare_repository(
        self,
        task: InstallationTask,
        sandbox: PodmanSandbox,
    ) -> list[CommandResult]:
        repository_url = shlex.quote(task.repository_url)
        repository_dir = shlex.quote(settings.repository_dir)
        commit_sha = shlex.quote(task.commit_sha.lower())
        commands = [
            "apt-get update",
            (
                "DEBIAN_FRONTEND=noninteractive apt-get install -y "
                "--no-install-recommends git ca-certificates"
            ),
            f"git clone --no-checkout --depth 1 {repository_url} {repository_dir}",
            f"git -C {repository_dir} fetch --depth 1 origin {commit_sha}",
            f"git -C {repository_dir} checkout --detach {commit_sha}",
            f'test "$(git -C {repository_dir} rev-parse HEAD)" = {commit_sha}',
        ]
        return self._run_until_failure(commands, sandbox, phase="setup")

    def _run_validation(
        self,
        task: InstallationTask,
        sandbox: PodmanSandbox,
    ) -> list[CommandResult]:
        return self._run_until_failure(
            task.validation_commands,
            sandbox,
            phase="validation",
            working_dir=settings.repository_dir,
        )

    @staticmethod
    def _run_until_failure(
        commands: list[str],
        sandbox: PodmanSandbox,
        *,
        phase: str,
        working_dir: str | None = None,
    ) -> list[CommandResult]:
        results: list[CommandResult] = []
        for command in commands:
            result = sandbox.execute_command(
                command,
                phase=phase,  # type: ignore[arg-type]
                working_dir=working_dir,
            )
            results.append(result)
            if result.exit_code != 0:
                break
        return results

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
    def _failure_message(stage: str, command: CommandResult) -> str:
        detail = command.stderr.strip() or command.stdout.strip() or "No output."
        return f"{stage} failed: {command.command}\n{detail}"

    @staticmethod
    def _phase_passed(commands: list[CommandResult], phase: str) -> bool:
        phase_commands = [command for command in commands if command.phase == phase]
        return bool(phase_commands) and all(
            command.exit_code == 0 for command in phase_commands
        )

    @staticmethod
    def _phase_count(commands: list[CommandResult], phase: str) -> int:
        return sum(command.phase == phase for command in commands)

    @staticmethod
    def _format_stream(commands: list[CommandResult], stream_name: str) -> str:
        parts: list[str] = []
        for command in commands:
            output = getattr(command, stream_name)
            if output:
                parts.append(
                    f"[{command.phase}] $ {command.command}\n{output}".rstrip()
                )
        return "\n\n".join(parts)
