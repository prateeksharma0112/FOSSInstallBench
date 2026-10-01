"""Domain models for one benchmark run."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from installbench.models.execution import AgentRunStatus, CommandExecution
from installbench.models.installation import (
    InstallationReport,
    ReportedInstallationOutcome,
)
from installbench.models.task import TaskSnapshot
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


class ResultModel(BaseModel):
    """Reject unknown fields so schema changes cannot silently discard evidence."""

    model_config = ConfigDict(extra="forbid")


class RunMetadata(ResultModel):
    run_id: str
    experiment_id: str
    run_number: int = Field(ge=1)
    started_at: datetime
    finished_at: datetime
    status: RunStatus
    error_message: str | None = None


class RunEnvironment(ResultModel):
    container_image: str
    container_engine: Literal["podman", "docker"]
    sandbox_mode: Literal["standard", "dind"]
    command_timeout_seconds: int


class InstallationAgentRun(ResultModel):
    model: str
    max_iterations: int
    status: AgentRunStatus | None = None
    reported_outcome: ReportedInstallationOutcome = (
        ReportedInstallationOutcome.UNKNOWN
    )
    error_message: str | None = None


class ValidationAgentRun(ResultModel):
    model: str
    max_iterations: int
    status: AgentRunStatus | None = None
    assessed_outcome: AssessedInstallationOutcome | None = None
    error_message: str | None = None


class AgentRuns(ResultModel):
    installation: InstallationAgentRun
    validation: ValidationAgentRun


class AgentArtifactPaths(ResultModel):
    """Paths relative to run.json, present only for artifacts actually written."""

    prompt_path: str
    response_path: str
    report_path: str | None = Field(
        default=None, exclude_if=lambda value: value is None
    )
    summary_path: str | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


class RunArtifacts(ResultModel):
    """Agent log path retains its existing workspace-relative meaning."""

    agent_run_data_path: str
    commands_path: str = "commands.json"
    installation: AgentArtifactPaths | None = Field(
        default=None, exclude_if=lambda value: value is None
    )
    validation: AgentArtifactPaths | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


class BenchmarkRunResult(ResultModel):
    """Canonical grouped run schema, with large evidence saved separately."""

    run: RunMetadata
    task: TaskSnapshot
    environment: RunEnvironment
    agents: AgentRuns
    metrics: RunMetrics
    artifacts: RunArtifacts
    command_executions: list[CommandExecution] = Field(
        default_factory=list, exclude=True
    )
    installation_report: InstallationReport | None = Field(default=None, exclude=True)
    validation_report: ValidationReport | None = Field(default=None, exclude=True)
    installation_prompt: str = Field(default="", exclude=True)
    installation_agent_response: str = Field(default="", exclude=True)
    validation_prompt: str = Field(default="", exclude=True)
    validation_agent_response: str = Field(default="", exclude=True)
