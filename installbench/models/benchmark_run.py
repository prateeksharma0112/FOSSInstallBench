"""Domain models for one benchmark run."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from installbench.models.execution import AgentRunStatus, CommandExecution
from installbench.models.installation import (
    InstallationReport,
    ReportedInstallationOutcome,
)
from installbench.models.validation import AssessedInstallationOutcome, ValidationReport


class RunStatus(StrEnum):
    """Outcome of the benchmark framework run itself."""

    COMPLETED = "completed"
    REPOSITORY_SETUP_FAILED = "repository_setup_failed"
    INSTALLATION_AGENT_FAILED = "installation_agent_failed"
    VALIDATION_AGENT_FAILED = "validation_agent_failed"
    SYSTEM_ERROR = "system_error"


class RunMetrics(BaseModel):
    """Execution metrics for a benchmark run."""

    duration_seconds: float
    repository_setup_duration_seconds: float
    installation_duration_seconds: float
    validation_duration_seconds: float
    command_count: int
    repository_setup_command_count: int
    installation_command_count: int
    validation_command_count: int


class BenchmarkRunResult(BaseModel):
    """Complete, reproducible evidence for one benchmark run."""

    run_id: str
    experiment_id: str
    run_number: int = Field(ge=1)
    dataset_id: str
    task_id: str
    task_name: str
    repository_url: str
    commit_sha: str
    container_image: str
    container_engine: Literal["podman", "docker"]
    sandbox_mode: Literal["standard", "dind"]
    installation_agent_model: str
    validation_agent_model: str
    workspace_path: str
    command_timeout_seconds: int
    max_installation_iterations: int
    max_validation_iterations: int
    started_at: datetime
    finished_at: datetime
    run_status: RunStatus
    installation_agent_status: AgentRunStatus | None = None
    installation_agent_reported_outcome: ReportedInstallationOutcome = (
        ReportedInstallationOutcome.UNKNOWN
    )
    installation_report: InstallationReport | None = None
    validation_agent_status: AgentRunStatus | None = None
    validation_agent_assessed_outcome: AssessedInstallationOutcome | None = None
    validation_report: ValidationReport | None = None
    metrics: RunMetrics
    command_executions: list[CommandExecution] = Field(default_factory=list)
    installation_prompt: str = ""
    installation_agent_response: str = ""
    installation_error_message: str | None = None
    validation_prompt: str = ""
    validation_agent_response: str = ""
    validation_error_message: str | None = None
    error_message: str | None = None
