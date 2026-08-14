"""Load installation tasks from the local task directory."""

import json
from pathlib import Path

from installbench.models.installation_task import InstallationTask


class TaskLoader:
    """Load and validate one installation task."""

    def __init__(self, tasks_dir: Path) -> None:
        self.tasks_dir = tasks_dir

    def load(self, task_id: str) -> InstallationTask:
        tasks_root = self.tasks_dir.resolve()
        task_dir = (tasks_root / task_id).resolve()

        if not task_dir.is_relative_to(tasks_root):
            raise ValueError(f"Invalid task ID: {task_id}")
        if not task_dir.is_dir():
            raise FileNotFoundError(f"Task not found: {task_id}")

        metadata_path = task_dir / "metadata.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"Task metadata not found: {metadata_path}")

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError(f"Task metadata must be a JSON object: {metadata_path}")

        documentation = self._load_documentation(task_dir / "docs")
        return InstallationTask.model_validate(
            {
                **metadata,
                "task_id": task_id,
                "documentation_files": documentation,
            }
        )

    @staticmethod
    def _load_documentation(docs_dir: Path) -> dict[str, str]:
        if not docs_dir.is_dir():
            return {}

        for guide_name in ("Installation.md", "installation.md"):
            guide_path = docs_dir / guide_name
            if guide_path.is_file():
                return {guide_name: guide_path.read_text(encoding="utf-8")}

        return {
            path.relative_to(docs_dir).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(docs_dir.rglob("*.md"))
        }
