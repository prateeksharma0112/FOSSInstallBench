"""Experiment settings loaded automatically from the ``.env`` file."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values with optional overrides from ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    tasks_dir: Path = Path("tasks")
    results_dir: Path = Path("results")
    workspace_dir: Path = Path("workspace")
    installation_prompt_path: Path = Path(
        "installbench/prompts/installation_prompt.txt"
    )

    default_container_image: str = "ubuntu:22.04"
    container_engine: Literal["podman", "docker"] = "podman"
    repository_dir: str = Field(
        default="/workspace/repository",
        description="Repository location inside the experiment container.",
    )
    command_timeout_seconds: int = Field(
        default=300,
        gt=0,
        description="Maximum runtime of one command before it is terminated.",
    )
    max_agent_iterations: int = Field(
        default=50,
        gt=0,
        description="Maximum number of OpenHands agent iterations in one run.",
    )

    llm_model: str = Field(description="LLM name in provider/model format.")
    llm_api_key: str = Field(description="API key used by the configured LLM.")


# Creating Settings reads and validates the values from .env.
settings = Settings()
