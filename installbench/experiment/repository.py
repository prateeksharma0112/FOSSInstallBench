"""Framework-controlled repository preparation."""

import shlex

from installbench.models.experiment_result import CommandResult
from installbench.models.installation_task import InstallationTask
from installbench.sandbox.protocol import Sandbox


def prepare_repository(
    task: InstallationTask,
    sandbox: Sandbox,
    repository_dir: str,
) -> list[CommandResult]:
    """Clone the pinned repository revision and return the command evidence."""

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

    results: list[CommandResult] = []
    for command in commands:
        result = sandbox.execute_command(command, phase="setup")
        results.append(result)
        if result.exit_code != 0:
            break
    return results
