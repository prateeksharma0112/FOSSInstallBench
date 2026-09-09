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


class ValidationReport(ValidationModel):
    """Independent assessment of an installation's resulting state."""

    assessed_outcome: AssessedInstallationOutcome = Field(
        description="Independently assessed installation outcome."
    )
    outcome_evidence: list[str] = Field(
        min_length=1,
        description="Observed command results supporting the assessed outcome.",
    )
    assessment_summary: str = Field(
        min_length=1,
        description="Validation actions, findings, assessment rationale, and limitations.",
    )


class ValidationAgentResult(ValidationModel):
    """Evidence returned after an independent validation run."""

    status: AgentRunStatus
    report: ValidationReport | None = None
    command_executions: list[CommandExecution] = Field(default_factory=list)
    prompt: str = ""
    final_response: str = ""
    error_message: str | None = None
