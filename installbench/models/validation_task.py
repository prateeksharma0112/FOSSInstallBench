"""Structured results from independent installation validation."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ValidationModel(BaseModel):
    """Strict base model for validator output."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ValidationVerdict(StrEnum):
    """Independent verdict about the resulting installation state."""

    VERIFIED_SUCCESS = "verified_success"
    VERIFIED_FAILURE = "verified_failure"
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

    verdict: ValidationVerdict
    summary: str = Field(min_length=1)
    checks: list[ValidationCheck] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
