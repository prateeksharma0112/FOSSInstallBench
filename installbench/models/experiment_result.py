"""
Domain models for Experiment Results.
"""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ExperimentMetrics(BaseModel):
    """Execution metrics for an experiment."""
    duration_seconds: float
    success: bool
    commands_executed_count: int


class ExperimentResult(BaseModel):
    """
    Comprehensive record of a single experiment run.
    """
    experiment_id: str
    task_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    metrics: ExperimentMetrics
    
    # A list of commands executed by the agent with their results
    # Each command is a dict with: command, exit_code, stdout, stderr
    commands: list[Any] = Field(default_factory=list)
    
    # Execution logs
    stdout: str = ""
    stderr: str = ""
    agent_log: str = ""
    
    error_message: str | None = None