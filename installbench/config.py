"""Benchmark settings loaded automatically from the ``.env`` file."""

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
    experiment_id: str = Field(
        default="default-experiment",
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$",
        description="Name shared by all runs in one experimental batch.",
    )
    installation_prompt_path: Path = Path("installbench/prompts/installation_prompt.md")
    validation_prompt_path: Path = Path("installbench/prompts/validation_prompt.md")

    default_container_image: str = "ubuntu:22.04"
    container_engine: Literal["podman", "docker"] = "podman"
    sandbox_mode: Literal["standard", "dind"] = "standard"
    repository_dir: str = Field(
        default="/workspace/repository",
        description="Repository location inside the benchmark container.",
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
    max_validator_iterations: int = Field(
        default=25,
        gt=0,
        description="Maximum number of OpenHands validator iterations in one run.",
    )

    llm_model: str = Field(description="LLM name in provider/model format.")
    llm_api_key: str = Field(description="API key used by the configured LLM.")
    llm_base_url: str | None = Field(
        default=None,
        description="Optional custom base URL for the configured LLM.",
    )

    validator_llm_model: str | None = Field(
        default=None,
        description="LLM used for independent installation validation.",
    )
    validator_llm_api_key: str | None = Field(
        default=None,
        description="API key used by the independent validation LLM.",
    )
    validator_llm_base_url: str | None = Field(
        default=None,
        description="Optional custom base URL for the validation LLM.",
    )


# Creating Settings reads and validates the values from .env.
settings = Settings()
