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

        flat_data = result.model_dump(
            mode="json",
            exclude={
                "command_executions",
                "installation_report",
                "installation_prompt",
                "installation_agent_response",
                "validation_report",
                "validation_prompt",
                "validation_agent_response",
                # These values are already present in the task metadata snapshot.
                "dataset_id",
                "task_name",
                "repository_url",
                "commit_sha",
            },
        )
        # Group run fields and store the dataset entry once, directly as the task.
        def take(*names: str) -> dict[str, Any]:
            return {name: flat_data.pop(name) for name in names}

        result_data = {
            "schema_version": 2,
            "run": take(
                "run_id", "experiment_id", "run_number", "started_at",
                "finished_at", "run_status", "error_message",
            ),
            "task": {
                "task_id": flat_data.pop("task_id"),
                **flat_data.pop("dataset_metadata"),
            },
            "environment": take(
                "container_image", "container_engine", "sandbox_mode",
                "command_timeout_seconds",
            ),
            "agents": {
                "installation": take(
                    "installation_agent_model", "max_installation_iterations",
                    "installation_agent_status", "installation_agent_reported_outcome",
                    "installation_error_message",
                ),
                "validation": take(
                    "validation_agent_model", "max_validation_iterations",
                    "validation_agent_status", "validation_agent_assessed_outcome",
                    "validation_error_message",
                ),
            },
            "metrics": flat_data.pop("metrics"),
            "artifacts": take("agent_run_data_path"),
        }
        if flat_data:
            raise ValueError(f"Ungrouped run result fields: {sorted(flat_data)}")

        # Artifact paths below are relative to run.json; only reference files written.
        artifacts = result_data["artifacts"]
        artifacts["commands_path"] = "commands.json"
        for phase in ("installation", "validation"):
            if getattr(result, f"{phase}_agent_status") is not None:
                paths = {
                    "prompt_path": f"{phase}/prompt.md",
                    "response_path": f"{phase}/final_response.txt",
                }
                if getattr(result, f"{phase}_report") is not None:
                    paths["report_path"] = f"{phase}/report.json"
                    if phase == "installation":
                        paths["summary_path"] = "installation/installation_summary.md"
                artifacts[phase] = paths
        self._write_json(
            run_dir / "commands.json",
            {
                "command_executions": [
                    execution.model_dump(mode="json")
                    for execution in result.command_executions
                ]
            },
        )

        if result.installation_agent_status is not None:
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
            if result.installation_report is not None:
                self._write_text(
                    run_dir / "installation" / "installation_summary.md",
                    result.installation_report.installation_summary,
                )
        if result.validation_agent_status is not None:
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
        self._write_json(run_path, result_data)

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
