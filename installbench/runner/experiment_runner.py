import time
import uuid
import structlog

from installbench.config import settings
from installbench.datasets.loader import DatasetLoader
from installbench.sandbox.docker_manager import DockerManager
from installbench.agents.adapter import AgentProtocol
from installbench.storage.json_storage import JsonStorage
from installbench.models.experiment_result import ExperimentResult, ExperimentMetrics

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

                # Extract results from agent response
                success = raw_results.get("success", False)
                commands = raw_results.get("commands", [])
                stdout = raw_results.get("stdout", "")
                stderr = raw_results.get("stderr", "")
                agent_log = raw_results.get("logs", "")
                error_msg = raw_results.get("error_message")
            except Exception as e:
                logger.exception("agent_invocation_failed", task_id=task_id)
                success = False
                commands = []
                stdout = ""
                stderr = str(e)
                agent_log = ""
                error_msg = str(e)

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
