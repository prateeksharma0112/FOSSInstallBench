"""Write benchmark run evidence to result files."""

import json
from pathlib import Path
from typing import Any, Protocol

import structlog

from installbench.models.benchmark_run import AgentArtifactPaths, BenchmarkRunResult
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
            result.run.experiment_id,
            result.task.task_id,
            result.run.run_number,
        )
        run_dir.mkdir(parents=True, exist_ok=True)
        run_path = run_dir / "run.json"
        if run_path.exists():
            raise FileExistsError(f"Run result already exists: {run_path}")

        self._write_json(
            run_dir / result.artifacts.commands_path,
            {
                "command_executions": [
                    execution.model_dump(mode="json")
                    for execution in result.command_executions
                ]
            },
        )

        result.artifacts.installation = None
        if result.agents.installation.status is not None:
            result.artifacts.installation = self._write_agent_artifacts(
                directory=run_dir / "installation",
                report=(
                    result.installation_report.model_dump(mode="json")
                    if result.installation_report is not None
                    else None
                ),
                prompt=result.installation_prompt,
                response=result.installation_agent_response,
            )
            if result.installation_report is not None:
                result.artifacts.installation.summary_path = (
                    "installation/installation_summary.md"
                )
                self._write_text(
                    run_dir / result.artifacts.installation.summary_path,
                    result.installation_report.installation_summary,
                )
        result.artifacts.validation = None
        if result.agents.validation.status is not None:
            result.artifacts.validation = self._write_agent_artifacts(
                directory=run_dir / "validation",
                report=(
                    result.validation_report.model_dump(mode="json")
                    if result.validation_report is not None
                    else None
                ),
                prompt=result.validation_prompt,
                response=result.validation_agent_response,
            )
        self._write_json(run_path, result.model_dump(mode="json"))

        logger.info("benchmark_run_result_saved", path=str(run_dir))

    @classmethod
    def _write_agent_artifacts(
        cls,
        *,
        directory: Path,
        report: dict[str, Any] | None,
        prompt: str,
        response: str,
    ) -> AgentArtifactPaths:
        directory.mkdir(exist_ok=True)
        paths = AgentArtifactPaths(
            prompt_path=f"{directory.name}/prompt.md",
            response_path=f"{directory.name}/final_response.txt",
        )
        if report is not None:
            paths.report_path = f"{directory.name}/report.json"
            cls._write_json(directory.parent / paths.report_path, report)
        cls._write_text(directory.parent / paths.prompt_path, prompt)
        cls._write_text(directory.parent / paths.response_path, response)
        return paths

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def _write_text(path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")
