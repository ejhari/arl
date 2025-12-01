"""Session management CLI commands."""

import click
from rich.console import Console

console = Console()


@click.group(name="session")
def session_group() -> None:
    """Manage research sessions."""
    pass


@session_group.command(name="start")
@click.option("--project", "project_id", required=True, help="Project ID")
def start_session(project_id: str) -> None:
    """Start a new research session."""
    # Will implement in Phase 2
    console.print(f"[yellow]Starting session for project: {project_id}[/yellow]")
    console.print("[yellow]Session management will be implemented in Phase 2[/yellow]")


@session_group.command(name="list")
@click.option("--project", "project_id", help="Filter by project ID")
def list_sessions(project_id: str | None) -> None:
    """List research sessions."""
    console.print("[yellow]Session listing will be implemented in Phase 2[/yellow]")
