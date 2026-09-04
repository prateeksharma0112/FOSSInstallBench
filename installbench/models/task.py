"""Domain models for benchmark tasks."""

from pydantic import BaseModel, ConfigDict, Field


class TaskMetadataModel(BaseModel):
    """Shared validation settings for task metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class SoftwareMetadata(TaskMetadataModel):
    """Software classification stored in a task's metadata file."""

    type: str = Field(min_length=1)
    primary_language: str = Field(min_length=1)
    platforms: list[str] = Field(min_length=1)


class InstallationGuideMetadata(TaskMetadataModel):
    """Provenance and size information for an installation guide."""

    source: str = Field(min_length=1)
    link: str = Field(min_length=1)
    language: str = Field(min_length=1)
    word_count: int = Field(ge=0)


class BenchmarkTask(TaskMetadataModel):
    """A repository pinned to an immutable revision with supplied setup guides."""

    task_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    dataset_id: str = Field(pattern=r"^P[0-9]{3}$")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    repository_url: str = Field(min_length=1)
    commit_sha: str = Field(pattern=r"^[0-9a-fA-F]{40}$")
    license: str = Field(min_length=1)
    software: SoftwareMetadata
    install_guide: InstallationGuideMetadata
    documentation_files: dict[str, str] = Field(min_length=1)
