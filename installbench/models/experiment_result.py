"""Domain models for one installation experiment."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

CommandPhase = Literal["setup", "agent"]


class ExperimentStatus(StrEnum):
    """Observable outcome of an experiment without claiming installation validity."""

    AGENT_FINISHED = "agent_finished"
    AGENT_FAILED = "agent_failed"
    SETUP_FAILED = "setup_failed"
    SYSTEM_ERROR = "system_error"


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

    finished: bool
    commands: list[CommandResult] = Field(default_factory=list)
    logs: str = ""
    prompt: str = ""
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
    agent_model: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: ExperimentStatus
    metrics: ExperimentMetrics
    commands: list[CommandResult] = Field(default_factory=list)
    agent_log: str = ""
    installation_prompt: str = ""
    error_message: str | None = None
