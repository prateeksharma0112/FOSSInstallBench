"""Command-line entry point for FOSSInstallBench."""

import typer
from rich.console import Console

from installbench.agents.openhands_installation_agent import OpenHandsInstallationAgent
from installbench.agents.openhands_validation_agent import OpenHandsValidationAgent
from installbench.benchmark_runner import BenchmarkRunner
from installbench.models.benchmark_run import RunStatus

app = typer.Typer(help="FOSSInstallBench - benchmark for AI-driven open-source installation")
console = Console()


@app.command(name="run")
def run_task(
    task_id: str = typer.Option(..., "--task-id", "-t", help="The ID of the task to run"),
) -> None:
    """Run an installation and independent-validation benchmark task."""
    console.print(
        f"[bold blue]Starting FOSSInstallBench[/bold blue] for task: "
        f"[bold green]{task_id}[/bold green]"
    )

    try:
        installation_agent = OpenHandsInstallationAgent()
        validation_agent = OpenHandsValidationAgent()
        runner = BenchmarkRunner(
            installation_agent=installation_agent,
            validation_agent=validation_agent,
        )
        run_result = runner.run(task_id=task_id)
    except Exception as exc:
        console.print(f"[bold red]Could not complete benchmark run:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    if run_result.run_status is RunStatus.COMPLETED:
        installation_agent_status = run_result.installation_agent_status
        validation_agent_status = run_result.validation_agent_status
        assessed_outcome = run_result.validation_agent_assessed_outcome
        console.print(f"[bold green]Benchmark run {run_result.run_id} completed.[/bold green]")
        console.print(
            "Installation agent: "
            f"{installation_agent_status.value if installation_agent_status else 'not_run'}; "
            f"reported outcome: {run_result.installation_agent_reported_outcome.value}."
        )
        console.print(
            "Validation agent: "
            f"{validation_agent_status.value if validation_agent_status else 'not_run'}; "
            "assessed outcome: "
            f"{assessed_outcome.value if assessed_outcome else 'not_available'}."
        )
        return

    console.print(
        f"[bold red]Benchmark run {run_result.run_id}: {run_result.run_status.value}.[/bold red]"
    )
    if run_result.error_message:
        console.print(f"[red]{run_result.error_message}[/red]")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
