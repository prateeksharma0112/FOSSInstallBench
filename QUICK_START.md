# InstallBench Quick Start

## Pipeline

Input: `tasks/<task-id>/docs/Installation.md`

Process:

1. Load task metadata and installation guide.
2. Start a fresh Docker container.
3. Run the OpenHands Software Agent SDK agent.
4. Execute OpenHands terminal actions inside the container.
5. Run task validation commands after the agent finishes.
6. Store command logs, metrics, stdout, and stderr.
7. Destroy the container.

Output: structured experiment results in `results/experiment_<id>/`.

## Run Redis

```powershell
installbench --task-id redis
```

OpenHands is the default agent. To run the simpler LLM command-planning baseline:

```powershell
installbench --task-id redis --agent llm-command
```

## Result Files

`summary.json`
: Experiment id, task id, timestamp, and top-level error.

`metrics.json`
: Duration, success flag, and command count.

`commands.json`
: Every executed command with exit code, stdout, stderr, and validation marker where relevant.

`logs/stdout.log`
: Combined stdout for executed commands.

`logs/stderr.log`
: Combined stderr for executed commands.

`logs/agent.log`
: Agent adapter details and validation summary.

## Add A Task

Create this structure:

```text
tasks/<software-name>/
  metadata.json
  docs/
    Installation.md
```

Example `metadata.json`:

```json
{
  "name": "Redis",
  "description": "Install Redis from the official Linux installation guide.",
  "validation_commands": [
    "redis-server --version",
    "redis-cli --version"
  ]
}
```

## Environment

Required:

```powershell
set LLM_API_KEY=your-api-key
set LLM_MODEL=gemini/gemini-3.5-flash
```

Optional:

```powershell
set INSTALLBENCH_MAX_COMMANDS=20
set INSTALLBENCH_LLM_RETRIES=2
set INSTALLBENCH_LLM_RETRY_DELAY_SECONDS=5
set INSTALLBENCH_OPENHANDS_MAX_ITERATIONS=40
set INSTALLBENCH_DEFAULT_DOCKER_IMAGE=ubuntu:22.04
```
