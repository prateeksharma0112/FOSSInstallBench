"""Domain model for source-based installation tasks."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class InstallationTask(BaseModel):
    """A repository pinned to an immutable revision with supplied setup guides."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    task_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    repository_url: str = Field(min_length=1)
    commit_sha: str = Field(pattern=r"^[0-9a-fA-F]{40}$")
    last_updated: date
    documentation_files: dict[str, str] = Field(min_length=1)
