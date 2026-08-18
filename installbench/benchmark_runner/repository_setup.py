"""Prepare the repository used by a benchmark run."""

import shlex

from installbench.models.benchmark_run import CommandExecution
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.protocol import Sandbox


def prepare_repository(
    task: InstallationTask,
    sandbox: Sandbox,
    repository_dir: str,
) -> list[CommandExecution]:
    """Clone the pinned repository revision and return command evidence."""

    quoted_url = shlex.quote(task.repository_url)
    quoted_dir = shlex.quote(repository_dir)
    quoted_commit = shlex.quote(task.commit_sha.lower())
    commands = [
        "apt-get update",
        (
            "DEBIAN_FRONTEND=noninteractive apt-get install -y "
            "--no-install-recommends git ca-certificates"
        ),
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
