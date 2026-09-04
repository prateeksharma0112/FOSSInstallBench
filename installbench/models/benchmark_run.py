"""Domain models for one benchmark run."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

RunPhase = Literal["repository_setup", "installation", "validation"]


class RunStatus(StrEnum):
    """Outcome of the benchmark framework run itself."""

    COMPLETED = "completed"
    REPOSITORY_SETUP_FAILED = "repository_setup_failed"
    INSTALLATION_AGENT_FAILED = "installation_agent_failed"
    SYSTEM_ERROR = "system_error"


class AgentRunStatus(StrEnum):
    """How an agent run ended."""

    COMPLETED = "completed"
    STOPPED = "stopped"
    ERROR = "error"


class InstallationOutcome(StrEnum):
    """Possible outcome of a software installation attempt."""

    SUCCESS = "success"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class FailureAttribution(StrEnum):
    """Primary cause of an unsuccessful installation attempt."""

    DOCUMENTATION = "DOCUMENTATION"
    AGENT = "AGENT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    EXTERNAL_RESOURCE = "EXTERNAL_RESOURCE"
    INDETERMINATE = "INDETERMINATE"


class InstallationReport(BaseModel):
    """Installation agent's structured account of the installation attempt."""

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


class InstallationAgentResult(BaseModel):
    """Evidence returned after an installation agent run."""

    status: AgentRunStatus
    outcome: InstallationOutcome = InstallationOutcome.UNKNOWN
    report: InstallationReport | None = None
    command_executions: list[CommandExecution] = Field(default_factory=list)
    prompt: str = ""
    final_response: str = ""
    error_message: str | None = None


class RunMetrics(BaseModel):
    """Execution metrics for a benchmark run."""

    duration_seconds: float
    repository_setup_duration_seconds: float
    installation_duration_seconds: float
    command_count: int
    repository_setup_command_count: int
    installation_command_count: int


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
    workspace_path: str
    command_timeout_seconds: int
    max_installation_iterations: int
    started_at: datetime
    finished_at: datetime
    run_status: RunStatus
    installation_agent_status: AgentRunStatus | None = None
    installation_agent_outcome: InstallationOutcome = InstallationOutcome.UNKNOWN
    installation_report: InstallationReport | None = None
    metrics: RunMetrics
    command_executions: list[CommandExecution] = Field(default_factory=list)
    installation_prompt: str = ""
    installation_agent_response: str = ""
    error_message: str | None = None
