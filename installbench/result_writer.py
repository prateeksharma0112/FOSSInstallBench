"""Write benchmark run evidence to result files."""

import json
from pathlib import Path
from typing import Any, Protocol

import structlog

from installbench.models.benchmark_run import BenchmarkRunResult
from installbench.run_layout import run_relative_path

logger = structlog.get_logger(__name__)


class ResultWriter(Protocol):
    """Interface for persisting a benchmark run result."""

    def write(self, result: BenchmarkRunResult) -> None: ...


class JsonResultWriter:
    """Write one normalized set of JSON and text artifacts per benchmark run."""

    def __init__(self, results_dir: Path) -> None:
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def write(self, result: BenchmarkRunResult) -> None:
        run_dir = self.results_dir / run_relative_path(
            result.experiment_id,
            result.task_id,
            result.run_number,
        )
        run_dir.mkdir(parents=True, exist_ok=True)
        result_path = run_dir / "result.json"
        if result_path.exists():
            raise FileExistsError(f"Run result already exists: {result_path}")

        result_data = result.model_dump(
            mode="json",
            exclude={
                "command_executions",
                "installation_report",
                "installation_prompt",
                "agent_final_response",
            },
        )
        self._write_json(result_path, result_data)
        if result.installation_report is not None:
            self._write_json(
                run_dir / "installation_report.json",
                result.installation_report.model_dump(mode="json"),
            )
        self._write_json(
            run_dir / "commands.json",
            {
                "command_executions": [
                    execution.model_dump(mode="json") for execution in result.command_executions
                ]
            },
        )
        self._write_text(run_dir / "installation_prompt.md", result.installation_prompt)
        self._write_text(run_dir / "agent_final_response.txt", result.agent_final_response)

        logger.info("benchmark_run_result_saved", path=str(run_dir))

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def _write_text(path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")
