"""Domain models for one installation experiment."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

CommandPhase = Literal["setup", "agent"]


class RunStatus(StrEnum):
    """Outcome of the benchmark framework run, independent of installation success."""

    COMPLETED = "completed"
    SETUP_FAILED = "setup_failed"
    AGENT_FAILED = "agent_failed"
    SYSTEM_ERROR = "system_error"


class AgentStatus(StrEnum):
    """How the agent execution itself ended."""

    FINISHED = "finished"
    FAILED = "failed"
    ERROR = "error"


class InstallationStatus(StrEnum):
    """Installation outcome, kept separate from agent and framework completion."""

    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class AgentInstallationReport(BaseModel):
    """Structured installation assessment reported by the agent."""

    outcome: InstallationStatus = Field(
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
    unresolved_issues: list[str] = Field(
        description="Errors or requirements that remained unresolved."
    )
    outcome_evidence: list[str] = Field(
        description="Observed command results supporting the reported outcome."
    )


class CommandResult(BaseModel):
    """One command executed inside the benchmark sandbox."""

    phase: CommandPhase
    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


class AgentExecutionResult(BaseModel):
    """Evidence returned after an agent run."""

    agent_status: AgentStatus
    installation_status: InstallationStatus = InstallationStatus.UNKNOWN
    installation_report: AgentInstallationReport | None = None
    commands: list[CommandResult] = Field(default_factory=list)
    logs: str = ""
    prompt: str = ""
    final_response: str = ""
    error_message: str | None = None


class ExperimentMetrics(BaseModel):
    """Execution metrics for an experiment."""

    duration_seconds: float
    setup_duration_seconds: float
    agent_duration_seconds: float
    commands_executed_count: int
    setup_commands_count: int
    agent_commands_count: int


class ExperimentResult(BaseModel):
    """Complete, reproducible evidence for one experiment run."""

    experiment_id: str
    task_id: str
    task_name: str
    repository_url: str
    commit_sha: str
    container_image: str
    container_engine: Literal["podman", "docker"]
    agent_model: str
    timestamp: datetime
    run_status: RunStatus
    agent_status: AgentStatus | None = None
    installation_status: InstallationStatus = InstallationStatus.UNKNOWN
    installation_report: AgentInstallationReport | None = None
    metrics: ExperimentMetrics
    commands: list[CommandResult] = Field(default_factory=list)
    agent_log: str = ""
    installation_prompt: str = ""
    agent_final_response: str = ""
    error_message: str | None = None
