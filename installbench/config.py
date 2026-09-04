"""Benchmark settings loaded automatically from the ``.env`` file."""

from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
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
    max_installation_iterations: int = Field(
        default=50,
        gt=0,
        validation_alias=AliasChoices(
            "MAX_INSTALLATION_ITERATIONS",
            "MAX_AGENT_ITERATIONS",
        ),
        description="Maximum number of installation-agent iterations in one run.",
    )
    max_validation_iterations: int = Field(
        default=25,
        gt=0,
        validation_alias=AliasChoices(
            "MAX_VALIDATION_ITERATIONS",
            "MAX_VALIDATOR_ITERATIONS",
        ),
        description="Maximum number of validation-agent iterations in one run.",
    )

    installation_llm_model: str = Field(
        validation_alias=AliasChoices("INSTALLATION_LLM_MODEL", "LLM_MODEL"),
        description="Installation LLM in provider/model format.",
    )
    installation_llm_api_key: str = Field(
        validation_alias=AliasChoices("INSTALLATION_LLM_API_KEY", "LLM_API_KEY"),
        description="API key used by the installation LLM.",
    )
    installation_llm_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "INSTALLATION_LLM_BASE_URL",
            "LLM_BASE_URL",
        ),
        description="Optional custom base URL for the installation LLM.",
    )

    validation_llm_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "VALIDATION_LLM_MODEL",
            "VALIDATOR_LLM_MODEL",
        ),
        description="LLM used for independent installation validation.",
    )
    validation_llm_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "VALIDATION_LLM_API_KEY",
            "VALIDATOR_LLM_API_KEY",
        ),
        description="API key used by the independent validation LLM.",
    )
    validation_llm_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "VALIDATION_LLM_BASE_URL",
            "VALIDATOR_LLM_BASE_URL",
        ),
        description="Optional custom base URL for the validation LLM.",
    )


# Creating Settings reads and validates the values from .env.
settings = Settings()
