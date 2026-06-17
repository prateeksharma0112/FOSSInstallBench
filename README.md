# InstallBench

InstallBench is a small experimental framework for evaluating how well software agents can follow installation guides.

For each task, it loads an `Installation.md` file, starts a fresh Docker container, runs an OpenHands Software Agent SDK agent against the guide, validates the result, and stores structured logs for analysis.

## Setup

```powershell
pip install -e ".[dev]"
```

Create a `.env` file or set environment variables:

```powershell
set LLM_API_KEY=your-api-key
set LLM_MODEL=gemini/gemini-3.5-flash
```

## Run

```powershell
installbench --task-id redis
```

OpenHands is the default agent. A simple LLM command-planning baseline is also available:

```powershell
installbench --task-id redis --agent llm-command
```

Results are written to `results/experiment_<id>/`.
