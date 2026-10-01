"""Domain models for benchmark tasks."""

from pydantic import BaseModel, ConfigDict, Field


class TaskMetadataModel(BaseModel):
    """Shared validation settings for task metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ProjectMetadata(TaskMetadataModel):
    """Project identity and classification from the dataset catalogue."""

    opencode_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    catalogue_url: str = Field(min_length=1)
    type: str = Field(min_length=1)
    platforms: list[str] = Field(min_length=1)


class RepositoryMetadata(TaskMetadataModel):
    """Source repository pinned to an immutable revision."""

    url: str = Field(min_length=1)
    commit_sha: str = Field(pattern=r"^[0-9a-fA-F]{40}$")
    license: str = Field(min_length=1)


class InstallationMetadata(TaskMetadataModel):
    """Installation classification supplied by the dataset."""

    complexity: str = Field(min_length=1)


class InstallationGuideMetadata(TaskMetadataModel):
    """Provenance and size information for an installation guide."""

    source: str = Field(min_length=1)
    url: str = Field(min_length=1)
    language: str = Field(min_length=1)
    word_count: int = Field(ge=0)


class BenchmarkTask(TaskMetadataModel):
    """A repository pinned to an immutable revision with supplied setup guides."""

    task_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    dataset_id: str = Field(pattern=r"^P[0-9]{3}$")
    project: ProjectMetadata
    repository: RepositoryMetadata
    installation: InstallationMetadata
    installation_guide: InstallationGuideMetadata
    documentation_files: dict[str, str] = Field(min_length=1)
