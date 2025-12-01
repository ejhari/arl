"""Research workflow CLI commands."""

import asyncio

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from arl.adk_agents.orchestrator.agent import create_orchestrator
from arl.core.project import ProjectService
from arl.core.session import SessionService

console = Console()


@click.group(name="research")
def research_group() -> None:
    """Run autonomous research workflows."""
    pass


@research_group.command(name="start")
@click.option("--project", "project_id", required=True, help="Project ID")
@click.option("--request", required=True, help="Research request or hypothesis")
def start_research(project_id: str, request: str) -> None:
    """Start a new research session."""
    console.print("[bold cyan]Starting new research session...[/bold cyan]\n")

    # Create session
    session_service = SessionService()
    project_service = ProjectService()

    # Verify project exists
    project = project_service.get_project(project_id)
    if not project:
        console.print(f"[red]✗[/red] Project not found: {project_id}")
        return

    # Create new session
    session = session_service.create_session(project_id)

    console.print(f"[green]✓[/green] Session created: {session.session_id}")
    console.print(f"  Project: {project.name}")
    console.print(f"  Status: {session.status.value}\n")

    # Execute first stage
    console.print("[bold]Executing research workflow...[/bold]\n")

    async def run_workflow():
        orchestrator = create_orchestrator()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running hypothesis generation...", total=None)

            result = await orchestrator.run(
                session_id=session.session_id,
                user_request=request,
            )

            progress.update(task, completed=True)

        return result

    # Run async workflow
    result = asyncio.run(run_workflow())

    # Display results
    stage = result.get("stage", "unknown")
    console.print(f"\n[bold green]✓[/bold green] Stage completed: {stage}\n")

    if "hypotheses" in result:
        hypotheses = result["hypotheses"]
        console.print(Panel(
            f"[bold]Generated Hypotheses[/bold]\n\n"
            f"{hypotheses.get('raw_output', '')[:500]}...",
            title="Hypothesis Generation",
            border_style="cyan",
        ))
        console.print(f"\nModel: {hypotheses.get('model_used', 'unknown')}")
        console.print(f"Tokens: {hypotheses.get('tokens_used', 0)}")

    console.print(f"\n[bold]Session ID:[/bold] {session.session_id}")
    console.print(f"[dim]Use 'arl research continue --session {session.session_id}' to proceed[/dim]")


@research_group.command(name="continue")
@click.option("--session", "session_id", required=True, help="Session ID")
@click.option("--request", default="continue", help="Next step request")
def continue_research(session_id: str, request: str) -> None:
    """Continue an existing research session."""
    console.print(f"[bold cyan]Continuing session {session_id}...[/bold cyan]\n")

    # Load session
    session_service = SessionService()
    session = session_service.get_session(session_id)

    if not session:
        console.print(f"[red]✗[/red] Session not found: {session_id}")
        return

    console.print(f"[green]✓[/green] Session loaded")
    console.print(f"  Status: {session.status.value}")
    console.print(f"  Created: {session.created_at}")
    console.print(f"  Updated: {session.updated_at}\n")

    # Execute next stage
    async def run_workflow():
        orchestrator = create_orchestrator()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running next workflow stage...", total=None)

            result = await orchestrator.run(
                session_id=session_id,
                user_request=request,
            )

            progress.update(task, completed=True)

        return result

    # Run async workflow
    result = asyncio.run(run_workflow())

    # Display results
    stage = result.get("stage", "unknown")
    console.print(f"\n[bold green]✓[/bold green] Stage completed: {stage}\n")

    if stage == "experiment_design":
        design = result.get("design", {})
        code = result.get("code", {})

        console.print(Panel(
            f"[bold]Experiment Protocol[/bold]\n\n"
            f"{design.get('protocol', '')[:400]}...",
            title="Experiment Design",
            border_style="green",
        ))

        console.print(f"\n[bold]Generated Code:[/bold]")
        console.print(f"  Length: {len(code.get('code', ''))} characters")
        console.print(f"  Valid: {code.get('validation', {}).get('valid', False)}")
        console.print(f"  Dependencies: {', '.join(code.get('dependencies', []))}")

    elif stage == "execution_complete":
        execution = result.get("execution", {})
        analysis = result.get("analysis", {})
        docker_available = result.get("docker_available", True)

        # Show Docker availability warning if needed
        if not docker_available:
            console.print("\n[yellow]⚠ Docker Not Available[/yellow]")
            console.print("[dim]Execution was skipped. To run experiments, ensure Docker is running.[/dim]\n")

        console.print(Panel(
            f"[bold]Execution Results[/bold]\n\n"
            f"Success: {execution.get('success', False)}\n"
            f"Exit Code: {execution.get('exit_code', -1)}\n"
            f"Artifacts: {len(execution.get('artifacts', []))}",
            title="Experiment Execution" + (" (Skipped)" if execution.get('skipped') else ""),
            border_style="yellow" if execution.get('skipped') else "blue",
        ))

        console.print(Panel(
            f"[bold]Analysis[/bold]\n\n"
            f"{analysis.get('raw_analysis', '')[:500]}...",
            title="Result Analysis",
            border_style="magenta",
        ))

    console.print(f"\n[bold]Session ID:[/bold] {session_id}")

    if stage != "execution_complete":
        console.print(f"[dim]Use 'arl research continue --session {session_id}' to proceed[/dim]")
    else:
        console.print("[bold green]Research cycle complete![/bold green]")


@research_group.command(name="run")
@click.option("--project", "project_id", required=True, help="Project ID")
@click.option("--request", required=True, help="Research request or hypothesis")
@click.option("--auto", is_flag=True, help="Run all stages automatically without pausing")
def run_research(project_id: str, request: str, auto: bool) -> None:
    """Run a complete research cycle (hypothesis → experiment → execution → analysis)."""
    console.print("[bold cyan]Running complete research cycle...[/bold cyan]\n")

    # Create session
    session_service = SessionService()
    project_service = ProjectService()

    # Verify project exists
    project = project_service.get_project(project_id)
    if not project:
        console.print(f"[red]✗[/red] Project not found: {project_id}")
        return

    # Create new session
    session = session_service.create_session(project_id)

    console.print(f"[green]✓[/green] Session created: {session.session_id}")
    console.print(f"  Project: {project.name}\n")

    async def run_complete_workflow():
        orchestrator = create_orchestrator()

        stages = [
            ("Hypothesis Generation", "hypothesis_generation"),
            ("Experiment Design", "experiment_design"),
            ("Execution & Analysis", "execution_complete"),
        ]

        results = []

        for stage_name, expected_stage in stages:
            console.print(f"[bold cyan]Stage: {stage_name}[/bold cyan]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Running {stage_name.lower()}...", total=None)

                result = await orchestrator.run(
                    session_id=session.session_id,
                    user_request=request if len(results) == 0 else "continue",
                )

                progress.update(task, completed=True)

            results.append(result)
            actual_stage = result.get("stage", "unknown")

            console.print(f"  [green]✓[/green] Completed: {actual_stage}\n")

            # Pause between stages if not auto mode
            if not auto and actual_stage != "execution_complete":
                if not click.confirm("Continue to next stage?", default=True):
                    console.print("[yellow]Workflow paused[/yellow]")
                    console.print(f"Resume with: arl research continue --session {session.session_id}")
                    return results

        return results

    # Run complete workflow
    results = asyncio.run(run_complete_workflow())

    # Display final summary
    console.print("\n" + "=" * 60)
    console.print("[bold green]RESEARCH CYCLE COMPLETE[/bold green]")
    console.print("=" * 60 + "\n")

    if len(results) >= 1 and "hypotheses" in results[0]:
        console.print("[bold]1. Hypothesis Generated[/bold]")
        hypotheses = results[0]["hypotheses"]
        console.print(f"   Model: {hypotheses.get('model_used', 'unknown')}")
        console.print(f"   Tokens: {hypotheses.get('tokens_used', 0)}\n")

    if len(results) >= 2 and "code" in results[1]:
        console.print("[bold]2. Experiment Designed & Code Generated[/bold]")
        code = results[1]["code"]
        console.print(f"   Code length: {len(code.get('code', ''))} chars")
        console.print(f"   Valid: {code.get('validation', {}).get('valid', False)}")
        console.print(f"   Dependencies: {len(code.get('dependencies', []))}\n")

    if len(results) >= 3 and "execution" in results[2]:
        console.print("[bold]3. Executed & Analyzed[/bold]")
        execution = results[2]["execution"]
        analysis = results[2]["analysis"]
        console.print(f"   Execution success: {execution.get('success', False)}")
        console.print(f"   Artifacts collected: {len(execution.get('artifacts', []))}")
        console.print(f"   Analysis model: {analysis.get('model_used', 'unknown')}\n")

    console.print(f"[bold]Session ID:[/bold] {session.session_id}")
    console.print(f"[bold]Project:[/bold] {project.name}")


@research_group.command(name="status")
@click.option("--session", "session_id", required=True, help="Session ID")
def show_status(session_id: str) -> None:
    """Show research session status and progress."""
    session_service = SessionService()
    session = session_service.get_session(session_id)

    if not session:
        console.print(f"[red]✗[/red] Session not found: {session_id}")
        return

    console.print("\n[bold]Session Status[/bold]\n")
    console.print(f"  Session ID: {session.session_id}")
    console.print(f"  Project ID: {session.project_id}")
    console.print(f"  Status: {session.status.value}")
    console.print(f"  Created: {session.created_at}")
    console.print(f"  Updated: {session.updated_at}")

    # Show state
    if session.state:
        console.print(f"\n[bold]Current State:[/bold]")
        current_stage = session.state.get("stage", "unknown")
        console.print(f"  Stage: {current_stage}")

        state_keys = list(session.state.keys())
        console.print(f"  Available data: {', '.join(state_keys)}")

    # Show events
    if session.events:
        console.print(f"\n[bold]Events:[/bold] {len(session.events)} logged")

    # Show checkpoints
    if session.checkpoints:
        console.print(f"\n[bold]Checkpoints:[/bold] {len(session.checkpoints)} saved")

    console.print()


@research_group.command(name="list")
@click.option("--project", "project_id", required=True, help="Project ID")
def list_sessions(project_id: str) -> None:
    """List all research sessions for a project."""
    session_service = SessionService()
    sessions = session_service.list_sessions(project_id)

    if not sessions:
        console.print("[yellow]No research sessions found[/yellow]")
        return

    console.print(f"\n[bold]Research Sessions for Project {project_id[:8]}...[/bold]\n")

    for session in sessions:
        stage = session.state.get("stage", "unknown") if session.state else "not started"
        console.print(f"[cyan]{session.session_id[:8]}...[/cyan] - {session.status.value} - {stage}")
        console.print(f"  Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}")
        console.print(f"  Updated: {session.updated_at.strftime('%Y-%m-%d %H:%M')}\n")
