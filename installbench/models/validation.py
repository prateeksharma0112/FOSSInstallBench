"""Structured results from independent installation validation."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from installbench.models.execution import AgentRunStatus, CommandExecution


class ValidationModel(BaseModel):
    """Strict base model for validator output."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AssessedInstallationOutcome(StrEnum):
    """Installation outcome assessed by the independent validation agent."""

    SUCCESS = "success"
    FAILURE = "failure"
    INCONCLUSIVE = "inconclusive"


class ValidationCheckStatus(StrEnum):
    """Observed result of one validation check."""

    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


class ValidationCheck(ValidationModel):
    """One command-backed check performed by the validator."""

    purpose: str = Field(min_length=1)
    command: str = Field(min_length=1)
    exit_code: int
    status: ValidationCheckStatus
    observation: str = Field(min_length=1)


class ValidationReport(ValidationModel):
    """Independent assessment of an installation's resulting state."""

    assessed_outcome: AssessedInstallationOutcome
    assessment_summary: str = Field(min_length=1)
    checks: list[ValidationCheck] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ValidationAgentResult(ValidationModel):
    """Evidence returned after an independent validation run."""

    status: AgentRunStatus
    report: ValidationReport | None = None
    command_executions: list[CommandExecution] = Field(default_factory=list)
    prompt: str = ""
    final_response: str = ""
    error_message: str | None = None
