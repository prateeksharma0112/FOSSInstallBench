"""
Domain models for Installation Tasks.
"""
from pydantic import BaseModel, ConfigDict, Field


class InstallationTask(BaseModel):
    """
    Represents a single benchmark sample for an installation experiment.
    """
    model_config = ConfigDict(frozen=True)
    
    task_id: str
    name: str
    description: str
    documentation_files: dict[str, str] = Field(default_factory=dict)
    validation_commands: list[str] = Field(default_factory=list)
