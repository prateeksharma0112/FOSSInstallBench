"""Domain models for experiment evidence and metrics."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


CommandPhase = Literal["setup", "agent", "validation"]


class CommandResult(BaseModel):
    """One command executed inside the benchmark sandbox."""

    phase: CommandPhase
    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


class AgentExecutionResult(BaseModel):
    """The agent's execution evidence, excluding benchmark validation."""

    completed: bool
    commands: list[CommandResult] = Field(default_factory=list)
    logs: str = ""
    error_message: str | None = None


class ExperimentMetrics(BaseModel):
    """Execution metrics for an experiment."""

    duration_seconds: float
    setup_duration_seconds: float
    agent_duration_seconds: float
    validation_duration_seconds: float
    success: bool
    commands_executed_count: int
    setup_commands_count: int
    agent_commands_count: int
    validation_commands_count: int


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
    metrics: ExperimentMetrics
    commands: list[CommandResult] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    agent_log: str = ""
    error_message: str | None = None
