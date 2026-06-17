import json
from pathlib import Path
import structlog
from installbench.models.installation_task import InstallationTask

logger = structlog.get_logger(__name__)

class DatasetLoader:
    def __init__(self, tasks_dir: Path) -> None:
        self.tasks_dir = tasks_dir

    def load_task(self, task_id: str) -> InstallationTask:
        task_path = self.tasks_dir / task_id
        if not task_path.exists():
            raise FileNotFoundError(f"Task {task_id} not found at {task_path}")

        # 1. Load Metadata
        metadata_path = task_path / "metadata.json"
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

        # 2. Load Docs
        docs = self._load_documentation(task_path / "docs")

        # 3. Return the model
        return InstallationTask(
            task_id=task_id,
            name=metadata.get("name"),
            description=metadata.get("description", ""),
            documentation_files=docs, # This contains Installation.md
            validation_commands=metadata.get("validation_commands", []),
        )

    def _load_documentation(self, docs_path: Path) -> dict[str, str]:
        docs = {}
        if docs_path.exists():
            for f in docs_path.glob("*.md"):
                docs[f.name] = f.read_text(encoding="utf-8")
        return docs
