"""Prepare the repository used by a benchmark run."""

import shlex

from installbench.models.execution import CommandExecution
from installbench.models.task import BenchmarkTask
from installbench.sandbox.protocol import Sandbox


def prepare_repository(
    task: BenchmarkTask,
    sandbox: Sandbox,
    installation_workspace_dir: str,
) -> list[CommandExecution]:
    """Prepare the pinned repository in the shared installation workspace."""

    quoted_url = shlex.quote(task.repository.url)
    quoted_dir = shlex.quote(installation_workspace_dir)
    quoted_commit = shlex.quote(task.repository.commit_sha.lower())
    commands = [
        f"git clone --no-checkout --depth 1 {quoted_url} {quoted_dir}",
        f"git -C {quoted_dir} fetch --depth 1 origin {quoted_commit}",
        f"git -C {quoted_dir} checkout --detach {quoted_commit}",
        f'test "$(git -C {quoted_dir} rev-parse HEAD)" = {quoted_commit}',
    ]

    command_executions: list[CommandExecution] = []
    for command in commands:
        command_execution = sandbox.execute_command(command, phase="repository_setup")
        command_executions.append(command_execution)
        if command_execution.exit_code != 0:
            break
    return command_executions
