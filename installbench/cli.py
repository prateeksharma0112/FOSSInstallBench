"""
Command Line Interface for InstallBench.
"""
import typer
from rich.console import Console
from installbench.runner.experiment_runner import ExperimentRunner
from installbench.agents.openhands_agent import OpenHandsAgent

app = typer.Typer(help="InstallBench - AI Agent Installation Benchmark Framework")
console = Console()

@app.command(name="run")
def run_task(
    task_id: str = typer.Option(..., "--task-id", "-t", help="The ID of the task to run")
) -> None:
    """Run an installation evaluation task."""
    console.print(f"[bold blue]Starting InstallBench[/bold blue] for task: [bold green]{task_id}[/bold green]")

    agent = OpenHandsAgent()
    runner = ExperimentRunner(agent=agent)
    
    try:
        result = runner.run(task_id=task_id)
        if result.metrics.success:
            console.print(
                f"[bold green]Experiment {result.experiment_id} passed.[/bold green]"
            )
        else:
            console.print(
                f"[bold red]Experiment {result.experiment_id} failed.[/bold red]"
            )
    except Exception as e:
        console.print(f"[bold red]Experiment failed:[/bold red] {e}")
        # Use a non-zero exit code for your thesis logs/automation to catch failures
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
