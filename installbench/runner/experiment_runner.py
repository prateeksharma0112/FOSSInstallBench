import time
import uuid
from typing import Any

import structlog

from installbench.agents.adapter import AgentProtocol
from installbench.config import settings
from installbench.datasets.loader import DatasetLoader
from installbench.models.experiment_result import ExperimentMetrics, ExperimentResult
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.docker_manager import DockerManager
from installbench.storage.json_storage import JsonStorage

logger = structlog.get_logger(__name__)


class ExperimentRunner:

    def __init__(self, agent: AgentProtocol) -> None:
        self.agent = agent
        self.dataset_loader = DatasetLoader(settings.tasks_dir)
        self.storage = JsonStorage(settings.results_dir)

    def run(self, task_id: str) -> ExperimentResult:
        experiment_id = str(uuid.uuid4())[:8]
        logger.info("starting_experiment", experiment_id=experiment_id, task_id=task_id)

        try:
            task = self.dataset_loader.load_task(task_id)
        except Exception as e:
            logger.exception("task_load_failed", task_id=task_id)
            raise e

        start_time = time.time()

        with DockerManager(base_image=settings.default_docker_image) as sandbox:

            installation_guide_text = task.documentation_files.get(
                "Installation.md", ""
            )

            try:
                logger.debug(
                    "invoking_agent",
                    task_id=task_id,
                    guide_length=len(installation_guide_text),
                )
                # We pass the formatted guide as the prompt parameter
                raw_results = self.agent.invoke(
                    task,
                    sandbox,
                    installation_guide_text,
                    experiment_id,
                )

                agent_completed = raw_results.get("completed", False)
                commands = raw_results.get("commands", [])
                agent_log = raw_results.get("logs", "")
                error_msg = raw_results.get("error_message")
            except Exception as e:
                logger.exception("agent_invocation_failed", task_id=task_id)
                agent_completed = False
                commands = []
                agent_log = ""
                error_msg = str(e)

            validation_results = (
                self._run_validation(task, sandbox) if agent_completed else []
            )
            commands.extend(validation_results)

            has_validation = bool(task.validation_commands)
            validation_passed = has_validation and all(
                result["exit_code"] == 0 for result in validation_results
            )
            success = agent_completed and validation_passed

            if agent_completed and not has_validation:
                error_msg = "Task has no validation commands."
            elif agent_completed and not validation_passed:
                failed_commands = [
                    result["command"]
                    for result in validation_results
                    if result["exit_code"] != 0
                ]
                error_msg = f"Validation failed: {', '.join(failed_commands)}"

            stdout = self._format_stream(commands, "stdout")
            stderr = self._format_stream(commands, "stderr")
            if error_msg and not stderr:
                stderr = error_msg

        duration = time.time() - start_time

        metrics = ExperimentMetrics(
            duration_seconds=duration,
            success=success,
            commands_executed_count=len(commands),
        )

        result = ExperimentResult(
            experiment_id=experiment_id,
            task_id=task_id,
            metrics=metrics,
            commands=commands,
            stdout=stdout,
            stderr=stderr,
            agent_log=agent_log,
            error_message=error_msg,
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

    def _run_validation(
        self,
        task: InstallationTask,
        sandbox: DockerManager,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for command in task.validation_commands:
            exit_code, stdout, stderr = sandbox.execute_command(
                command,
                working_dir="/workspace",
            )
            results.append(
                {
                    "command": command,
                    "exit_code": exit_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "validation": True,
                }
            )
        return results

    def _format_stream(
        self,
        results: list[dict[str, Any]],
        stream_name: str,
    ) -> str:
        parts = []
        for result in results:
            output = result.get(stream_name, "")
            if output:
                parts.append(f"$ {result['command']}\n{output}".rstrip())
        return "\n\n".join(parts)
