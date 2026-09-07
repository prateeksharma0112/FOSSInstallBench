"""Benchmark settings loaded automatically from the ``.env`` file."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values with optional overrides from ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Run inputs, outputs, and identity
    tasks_dir: Path = Path("tasks")
    results_dir: Path = Path("results")
    agent_run_data_dir: Path = Path("workspace")
    experiment_id: str = Field(
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$",
        description="Name shared by all runs in one experimental batch.",
    )
    installation_prompt_path: Path = Path("installbench/prompts/installation_prompt.md")
    validation_prompt_path: Path = Path("installbench/prompts/validation_prompt.md")

    # Sandbox and execution limits
    default_container_image: str = "ubuntu:22.04"
    container_engine: Literal["podman", "docker"] = "podman"
    sandbox_mode: Literal["standard", "dind"] = "standard"
    installation_workspace_dir: str = Field(
        default="/workspace",
        description=(
            "Shared container directory used for repository setup, installation, "
            "and validation."
        ),
    )
    command_timeout_seconds: int = Field(
        default=600,
        gt=0,
        description="Maximum runtime of one command before it is terminated.",
    )
    max_installation_iterations: int = Field(
        default=300,
        gt=0,
        description="Maximum number of installation-agent iterations in one run.",
    )
    max_validation_iterations: int = Field(
        default=200,
        gt=0,
        description="Maximum number of validation-agent iterations in one run.",
    )

    # Installation agent model
    installation_llm_model: str = Field(
        description="Installation LLM in provider/model format.",
    )
    installation_llm_api_key: str | None = Field(
        default=None,
        description="Optional API key used by the installation LLM.",
    )
    installation_llm_base_url: str | None = Field(
        default=None,
        description="Optional custom base URL for the installation LLM.",
    )
    installation_llm_reasoning_effort: (
        Literal["none", "low", "medium", "high", "xhigh"] | None
    ) = Field(
        default=None,
        description="Optional reasoning effort for the installation LLM.",
    )

    # Validation agent model
    validation_llm_model: str = Field(
        description="LLM used for independent installation validation.",
    )
    validation_llm_api_key: str | None = Field(
        default=None,
        description="API key used by the independent validation LLM.",
    )
    validation_llm_base_url: str | None = Field(
        default=None,
        description="Optional custom base URL for the validation LLM.",
    )
    validation_llm_reasoning_effort: (
        Literal["none", "low", "medium", "high", "xhigh"] | None
    ) = Field(
        default=None,
        description="Optional reasoning effort for the validation LLM.",
    )


# Creating Settings reads and validates the values from .env.
settings = Settings()
