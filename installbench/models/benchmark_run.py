"""Domain models for one benchmark run."""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Literal

from pydantic import BaseModel, Field

RunPhase = Literal["repository_setup", "agent"]


class RunStatus(StrEnum):
    """Outcome of the benchmark framework run itself."""

    COMPLETED = "completed"
    REPOSITORY_SETUP_FAILED = "repository_setup_failed"
    AGENT_RUN_FAILED = "agent_run_failed"
    SYSTEM_ERROR = "system_error"


class AgentRunStatus(StrEnum):
    """How the installation agent run ended."""

    COMPLETED = "completed"
    STOPPED = "stopped"
    ERROR = "error"


class InstallationOutcome(StrEnum):
    """Observed outcome of the software installation attempt."""

    SUCCESS = "success"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class FailureAttribution(str, Enum):
    """Primary cause of an unsuccessful installation attempt."""

    DOCUMENTATION = "DOCUMENTATION"
    AGENT = "AGENT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    EXTERNAL_RESOURCE = "EXTERNAL_RESOURCE"
    INDETERMINATE = "INDETERMINATE"


class InstallationReport(BaseModel):
    """Structured installation assessment reported by the agent."""

    outcome: InstallationOutcome = Field(
        description="Agent-reported installation outcome."
    )
    installation_summary: str = Field(
        description="Brief account of what was completed during installation."
    )
    additional_actions: list[str] = Field(
        description="Actions taken that were not stated in the installation guide."
    )
    verification: str = Field(
        description="Verification command, exit code, and observed result."
    )
    outcome_evidence: list[str] = Field(
        description="Observed command results supporting the reported outcome."
    )
    failure_mode: str | None = Field(
        default=None,
        description="Evidence-based failure description; null for a successful installation.",
    )
    failure_attribution: FailureAttribution | None = Field(
        default=None,
        description="Primary failure attribution; null for a successful installation.",
    )


class CommandExecution(BaseModel):
    """One command executed inside the benchmark sandbox."""

    phase: RunPhase
    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


class AgentRunResult(BaseModel):
    """Evidence returned after an installation agent run."""

    agent_run_status: AgentRunStatus
    installation_outcome: InstallationOutcome = InstallationOutcome.UNKNOWN
    installation_report: InstallationReport | None = None
    command_executions: list[CommandExecution] = Field(default_factory=list)
    installation_prompt: str = ""
    agent_final_response: str = ""
    error_message: str | None = None


class RunMetrics(BaseModel):
    """Execution metrics for a benchmark run."""

    duration_seconds: float
    repository_setup_duration_seconds: float
    agent_run_duration_seconds: float
    command_count: int
    repository_setup_command_count: int
    agent_command_count: int


class BenchmarkRunResult(BaseModel):
    """Complete, reproducible evidence for one benchmark run."""

    run_id: str
    dataset_id: str
    task_id: str
    task_name: str
    repository_url: str
    commit_sha: str
    container_image: str
    container_engine: Literal["podman", "docker"]
    agent_model: str
    started_at: datetime
    finished_at: datetime
    run_status: RunStatus
    agent_run_status: AgentRunStatus | None = None
    installation_outcome: InstallationOutcome = InstallationOutcome.UNKNOWN
    installation_report: InstallationReport | None = None
    metrics: RunMetrics
    command_executions: list[CommandExecution] = Field(default_factory=list)
    installation_prompt: str = ""
    agent_final_response: str = ""
    error_message: str | None = None
