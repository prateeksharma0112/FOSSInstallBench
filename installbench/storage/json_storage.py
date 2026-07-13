"""
Handles persisting experiment results locally.
"""
import json
from pathlib import Path

import structlog

from installbench.models.experiment_result import ExperimentResult

logger = structlog.get_logger(__name__)


class JsonStorage:
    """Stores experiment results locally strictly using JSON and text files."""
    
    def __init__(self, base_results_dir: Path) -> None:
        self.base_results_dir = base_results_dir
        self.base_results_dir.mkdir(parents=True, exist_ok=True)

    def store(self, result: ExperimentResult) -> None:
        """
        Writes an ExperimentResult to disk in a structured folder.
        
        Args:
            result: The completed experiment data.
        """
        experiment_dir = self.base_results_dir / f"experiment_{result.experiment_id}"
        experiment_dir.mkdir(parents=True, exist_ok=True)
        
        logs_dir = experiment_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # 1. Summary JSON
        summary_data = {
            "experiment_id": result.experiment_id,
            "task_id": result.task_id,
            "task_name": result.task_name,
            "repository_url": result.repository_url,
            "commit_sha": result.commit_sha,
            "container_image": result.container_image,
            "agent_model": result.agent_model,
            "timestamp": result.timestamp.isoformat(),
            "success": result.metrics.success,
            "error_message": result.error_message,
        }
        self._write_json(experiment_dir / "summary.json", summary_data)
        
        # 2. Metrics JSON
        self._write_json(
            experiment_dir / "metrics.json", result.metrics.model_dump(mode="json")
        )
        
        # 3. Commands JSON
        self._write_json(
            experiment_dir / "commands.json",
            {"commands": [command.model_dump(mode="json") for command in result.commands]},
        )

        # Complete machine-readable record
        self._write_json(
            experiment_dir / "result.json",
            result.model_dump(mode="json"),
        )
        
        # 4. Logs
        self._write_text(logs_dir / "stdout.log", result.stdout)
        self._write_text(logs_dir / "stderr.log", result.stderr)
        self._write_text(logs_dir / "agent.log", result.agent_log)
        
        logger.info("stored_experiment_results", path=str(experiment_dir))

    def _write_json(self, path: Path, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _write_text(self, path: Path, text: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
