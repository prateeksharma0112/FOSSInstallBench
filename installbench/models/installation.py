"""Structured results from the installation agent."""

from enum import StrEnum

from pydantic import BaseModel, Field

from installbench.models.execution import AgentRunStatus, CommandExecution


class ReportedInstallationOutcome(StrEnum):
    """Installation outcome reported by the installation agent."""

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

    reported_outcome: ReportedInstallationOutcome = Field(
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
    reported_outcome_evidence: list[str] = Field(
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


class InstallationAgentResult(BaseModel):
    """Evidence returned after an installation agent run."""

    status: AgentRunStatus
    reported_outcome: ReportedInstallationOutcome = ReportedInstallationOutcome.UNKNOWN
    report: InstallationReport | None = None
    command_executions: list[CommandExecution] = Field(default_factory=list)
    prompt: str = ""
    final_response: str = ""
    error_message: str | None = None
