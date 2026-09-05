"""Allocate matching result and agent-run-data directories."""

import re
from dataclasses import dataclass
from pathlib import Path

_RUN_DIRECTORY_PATTERN = re.compile(r"^run-(\d+)$")


@dataclass(frozen=True)
class RunLayout:
    """Identity and storage locations allocated to one benchmark run."""

    experiment_id: str
    task_id: str
    run_number: int
    run_id: str
    agent_run_data_dir: Path


def run_relative_path(experiment_id: str, task_id: str, run_number: int) -> Path:
    """Return the shared path below the result and agent-run-data roots."""

    return Path(experiment_id) / task_id / f"run-{run_number:02d}"


def _existing_run_numbers(*task_dirs: Path) -> set[int]:
    run_numbers: set[int] = set()
    for task_dir in task_dirs:
        if not task_dir.is_dir():
            continue
        for path in task_dir.iterdir():
            match = _RUN_DIRECTORY_PATTERN.fullmatch(path.name)
            if path.is_dir() and match:
                run_numbers.add(int(match.group(1)))
    return run_numbers


def allocate_run_layout(
    *,
    experiment_id: str,
    task_id: str,
    results_dir: Path,
    agent_run_data_dir: Path,
) -> RunLayout:
    """Create matching directories using the next number found across both roots."""

    result_task_dir = results_dir / experiment_id / task_id
    agent_run_data_task_dir = agent_run_data_dir / experiment_id / task_id
    run_numbers = _existing_run_numbers(result_task_dir, agent_run_data_task_dir)
    run_number = max(run_numbers, default=0) + 1
    relative_path = run_relative_path(experiment_id, task_id, run_number)
    run_name = relative_path.name

    result_run_dir = results_dir / relative_path
    agent_run_data_run_dir = agent_run_data_dir / relative_path
    result_run_dir.mkdir(parents=True, exist_ok=False)
    agent_run_data_run_dir.mkdir(parents=True, exist_ok=False)

    return RunLayout(
        experiment_id=experiment_id,
        task_id=task_id,
        run_number=run_number,
        run_id=f"{experiment_id}__{task_id}__{run_name}",
        agent_run_data_dir=agent_run_data_run_dir,
    )
