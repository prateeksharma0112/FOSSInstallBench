"""Command-line entry point for FOSSInstallBench."""

import typer
from rich.console import Console

from installbench.agents.openhands_agent import OpenHandsAgent
from installbench.benchmark_runner import BenchmarkRunner
from installbench.models.benchmark_run import RunStatus

app = typer.Typer(help="FOSSInstallBench - benchmark for AI-driven open-source installation")
console = Console()


@app.command(name="run")
def run_task(
    task_id: str = typer.Option(..., "--task-id", "-t", help="The ID of the task to run"),
) -> None:
    """Run an installation evaluation task."""
    console.print(
        f"[bold blue]Starting FOSSInstallBench[/bold blue] for task: "
        f"[bold green]{task_id}[/bold green]"
    )

    try:
        agent = OpenHandsAgent()
        runner = BenchmarkRunner(agent=agent)
        run_result = runner.run(task_id=task_id)
    except Exception as exc:
        console.print(f"[bold red]Could not complete benchmark run:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    if run_result.run_status is RunStatus.COMPLETED:
        agent_run_status = run_result.agent_run_status
        console.print(f"[bold green]Benchmark run {run_result.run_id} completed.[/bold green]")
        console.print(
            f"Agent run: {agent_run_status.value if agent_run_status else 'not_run'}; "
            f"installation outcome: {run_result.installation_outcome.value}."
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
