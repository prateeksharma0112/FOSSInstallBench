"""Models shared across benchmark execution phases."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

RunPhase = Literal["repository_setup", "installation", "validation"]


class AgentRunStatus(StrEnum):
    """How an agent run ended."""

    COMPLETED = "completed"
    STOPPED = "stopped"
    ERROR = "error"


class CommandExecution(BaseModel):
    """One command executed inside the benchmark sandbox."""

    phase: RunPhase
    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
