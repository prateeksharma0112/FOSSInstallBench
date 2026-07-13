import json
from pathlib import Path

import structlog

from installbench.models.installation_task import InstallationTask

logger = structlog.get_logger(__name__)


class DatasetLoader:
    def __init__(self, tasks_dir: Path) -> None:
        self.tasks_dir = tasks_dir

    def load_task(self, task_id: str) -> InstallationTask:
        tasks_root = self.tasks_dir.resolve()
        task_path = (tasks_root / task_id).resolve()
        if not task_path.is_relative_to(tasks_root):
            raise ValueError(f"Invalid task ID: {task_id}")
        if not task_path.is_dir():
            raise FileNotFoundError(f"Task {task_id} not found at {task_path}")

        metadata_path = task_path / "metadata.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"Task metadata not found at {metadata_path}")
        with metadata_path.open(encoding="utf-8") as file:
            metadata = json.load(file)
        if not isinstance(metadata, dict):
            raise ValueError(f"Task metadata must be a JSON object: {metadata_path}")

        docs = self._load_documentation(task_path / "docs")
        return InstallationTask.model_validate(
            {"task_id": task_id, "documentation_files": docs, **metadata}
        )

    def _load_documentation(self, docs_path: Path) -> dict[str, str]:
        docs: dict[str, str] = {}
        if docs_path.is_dir():
            for file in sorted(docs_path.rglob("*.md")):
                relative_name = file.relative_to(docs_path).as_posix()
                docs[relative_name] = file.read_text(encoding="utf-8")
        return docs
