"""Command-line entry point for InstallBench."""

import typer
from rich.console import Console

from installbench.agents.openhands_agent import OpenHandsAgent
from installbench.experiment.runner import ExperimentRunner
from installbench.models.experiment_result import RunStatus

app = typer.Typer(help="InstallBench - AI Agent Installation Benchmark Framework")
console = Console()


@app.command(name="run")
def run_task(
    task_id: str = typer.Option(..., "--task-id", "-t", help="The ID of the task to run")
) -> None:
    """Run an installation evaluation task."""
    console.print(
        f"[bold blue]Starting InstallBench[/bold blue] for task: "
        f"[bold green]{task_id}[/bold green]"
    )

    try:
        agent = OpenHandsAgent()
        runner = ExperimentRunner(agent=agent)
        result = runner.run(task_id=task_id)
    except Exception as exc:
        console.print(f"[bold red]Could not run experiment:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    if result.run_status is RunStatus.COMPLETED:
        console.print(
            f"[bold green]Experiment {result.experiment_id} completed.[/bold green]"
        )
        console.print(
            f"Agent: {result.agent_status.value if result.agent_status else 'not_run'}; "
            f"installation: {result.installation_status.value}."
        )
        return

    console.print(
        f"[bold red]Experiment {result.experiment_id}: "
        f"{result.run_status.value}.[/bold red]"
    )
    if result.error_message:
        console.print(f"[red]{result.error_message}[/red]")
    raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
