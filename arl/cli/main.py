"""ARL Command-line interface."""

import click
from rich.console import Console

from arl import __version__
from arl.cli.a2a_commands import a2a_cli
from arl.cli.paper_commands import paper_group
from arl.cli.project_commands import project_group
from arl.cli.research_commands import research_group
from arl.cli.session_commands import session_group
from arl.storage.database import init_db

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="arl")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """AI Autonomous Research Lab - Multi-agent scientific research automation."""
    # Ensure database is initialized
    init_db()
    ctx.ensure_object(dict)


# Register command groups
cli.add_command(project_group)
cli.add_command(session_group)
cli.add_command(paper_group)
cli.add_command(research_group)
cli.add_command(a2a_cli)


@cli.command()
def init() -> None:
    """Initialize ARL environment and database."""
    console.print("[bold green]Initializing ARL...[/bold green]")
    init_db()
    console.print("[bold green]✓[/bold green] Database initialized")
    console.print("[bold green]✓[/bold green] ARL ready to use")


if __name__ == "__main__":
    cli()
