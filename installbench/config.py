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
    
    default_docker_image: str = "ubuntu:22.04"
    agent_timeout_seconds: int = 3600


settings = Settings()
