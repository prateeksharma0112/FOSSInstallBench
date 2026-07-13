"""
Configuration management for InstallBench.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings."""
    
    model_config = SettingsConfigDict(env_prefix="INSTALLBENCH_", env_file=".env", extra="ignore")
    
    base_dir: Path = Path(__file__).parent.parent
    tasks_dir: Path = base_dir / "tasks"
    results_dir: Path = base_dir / "results"
    workspace_dir: Path = base_dir / "workspace"

    default_container_image: str = "ubuntu:22.04"
    repository_dir: str = "/workspace/repository"
    command_timeout_seconds: int = 300
    max_agent_iterations: int = 50


settings = Settings()
