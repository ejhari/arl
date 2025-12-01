"""Project management CLI commands."""

import click
from rich.console import Console
from rich.table import Table

from arl.core.project import ProjectService
from arl.storage.models import DomainType

console = Console()


@click.group(name="project")
def project_group() -> None:
    """Manage research projects."""
    pass


@project_group.command(name="create")
@click.option("--name", required=True, help="Project name")
@click.option(
    "--domain",
    type=click.Choice(["cs", "biology", "physics", "general"]),
    default="general",
    help="Scientific domain",
)
@click.option("--objectives", help="Research objectives")
def create_project(name: str, domain: str, objectives: str | None) -> None:
    """Create a new research project."""
    service = ProjectService()
    project = service.create_project(
        name=name,
        domain=DomainType(domain),
        objectives=objectives,
    )
    console.print(f"[bold green]✓[/bold green] Project created: {project.project_id}")
    console.print(f"  Name: {project.name}")
    console.print(f"  Domain: {project.domain.value}")


@project_group.command(name="list")
def list_projects() -> None:
    """List all projects."""
    service = ProjectService()
    projects = service.list_projects()

    if not projects:
        console.print("[yellow]No projects found[/yellow]")
        return

    table = Table(title="Research Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Domain", style="magenta")
    table.add_column("Created", style="blue")

    for project in projects:
        table.add_row(
            project.project_id[:8] + "...",
            project.name,
            project.domain.value,
            project.created_at.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


@project_group.command(name="show")
@click.argument("project_id")
def show_project(project_id: str) -> None:
    """Show project details."""
    service = ProjectService()
    project = service.get_project(project_id)

    if not project:
        console.print(f"[red]✗[/red] Project not found: {project_id}")
        return

    console.print(f"[bold]Project: {project.name}[/bold]")
    console.print(f"  ID: {project.project_id}")
    console.print(f"  Domain: {project.domain.value}")
    console.print(f"  Created: {project.created_at}")
    if project.objectives:
        console.print(f"  Objectives: {project.objectives}")
    console.print(f"  Sessions: {len(project.sessions)}")
    console.print(f"  Papers: {len(project.papers)}")
