"""Persist experiment evidence as JSON and text files."""

import json
from pathlib import Path
from typing import Any, Protocol

import structlog

from installbench.models.experiment_result import ExperimentResult

logger = structlog.get_logger(__name__)


class ResultStorage(Protocol):
    """Storage contract used by the experiment runner."""

    def save(self, result: ExperimentResult) -> None: ...


class JsonStorage:
    """Store one normalized set of artifacts for each experiment."""

    def __init__(self, base_results_dir: Path) -> None:
        self.base_results_dir = base_results_dir
        self.base_results_dir.mkdir(parents=True, exist_ok=True)

    def save(self, result: ExperimentResult) -> None:
        experiment_dir = self.base_results_dir / f"experiment_{result.experiment_id}"
        experiment_dir.mkdir(parents=True, exist_ok=True)

        result_data = result.model_dump(
            mode="json",
            exclude={"commands", "agent_log", "installation_prompt"},
        )
        self._write_json(experiment_dir / "result.json", result_data)
        self._write_json(
            experiment_dir / "commands.json",
            {"commands": [command.model_dump(mode="json") for command in result.commands]},
        )
        self._write_text(experiment_dir / "agent.log", result.agent_log)
        self._write_text(
            experiment_dir / "installation_prompt.txt",
            result.installation_prompt,
        )

        logger.info("stored_experiment_results", path=str(experiment_dir))

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def _write_text(path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")
