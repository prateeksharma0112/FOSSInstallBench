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
        run_path = run_dir / "run.json"
        if run_path.exists():
            raise FileExistsError(f"Run result already exists: {run_path}")

        result_data = result.model_dump(
            mode="json",
            exclude={
                "command_executions",
                "installation_report",
                "installation_prompt",
                "installation_agent_response",
                "validation_report",
                "validation_prompt",
                "validation_agent_response",
            },
        )
        self._write_json(run_path, result_data)

        self._write_json(
            run_dir / "commands.json",
            {
                "command_executions": [
                    execution.model_dump(mode="json")
                    for execution in result.command_executions
                ]
            },
        )

        self._write_agent_artifacts(
            directory=run_dir / "installation",
            report=(
                result.installation_report.model_dump(mode="json")
                if result.installation_report is not None
                else None
            ),
            prompt=result.installation_prompt,
            response=result.installation_agent_response,
        )
        self._write_agent_artifacts(
            directory=run_dir / "validation",
            report=(
                result.validation_report.model_dump(mode="json")
                if result.validation_report is not None
                else None
            ),
            prompt=result.validation_prompt,
            response=result.validation_agent_response,
        )

        logger.info("benchmark_run_result_saved", path=str(run_dir))

    @classmethod
    def _write_agent_artifacts(
        cls,
        *,
        directory: Path,
        report: dict[str, Any] | None,
        prompt: str,
        response: str,
    ) -> None:
        directory.mkdir(exist_ok=True)
        if report is not None:
            cls._write_json(directory / "report.json", report)
        cls._write_text(directory / "prompt.md", prompt)
        cls._write_text(directory / "final_response.txt", response)

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def _write_text(path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")
