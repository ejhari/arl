"""CLI commands for A2A (Agent-to-Agent) protocol management."""

import asyncio
import logging

import click
from rich.console import Console
from rich.table import Table

from arl.a2a.server import create_a2a_server, start_all_agent_servers
from arl.config.a2a_config import a2a_config, get_agent_port, get_agent_url

console = Console()
logger = logging.getLogger(__name__)


@click.group(name="a2a")
def a2a_cli():
    """Manage A2A (Agent-to-Agent) protocol servers and communication."""
    pass


@a2a_cli.command(name="status")
def status():
    """Show A2A configuration and status."""
    console.print("\n[bold]A2A Protocol Configuration[/bold]\n", style="cyan")

    # Configuration table
    config_table = Table(show_header=True, header_style="bold magenta")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")

    config_table.add_row("Enabled", str(a2a_config.enabled))
    config_table.add_row("Deployment Mode", a2a_config.deployment_mode)
    config_table.add_row("Host", a2a_config.host)
    config_table.add_row("Base Port", str(a2a_config.base_port))
    config_table.add_row("Auth Scheme", a2a_config.auth_scheme)
    config_table.add_row("Timeout", f"{a2a_config.timeout_seconds}s")

    console.print(config_table)

    # Agent endpoints table
    console.print("\n[bold]Agent Endpoints[/bold]\n", style="cyan")

    agents_table = Table(show_header=True, header_style="bold magenta")
    agents_table.add_column("Agent", style="cyan")
    agents_table.add_column("Port", style="yellow")
    agents_table.add_column("URL", style="green")

    agents = ["hypothesis", "experiment", "code_gen", "execution", "analysis"]
    for agent in agents:
        port = get_agent_port(agent)
        url = get_agent_url(agent)
        agents_table.add_row(agent, str(port), url)

    console.print(agents_table)


@a2a_cli.command(name="start")
@click.option(
    "--agent",
    type=click.Choice(["hypothesis", "experiment", "code_gen", "execution", "analysis", "all"]),
    default="all",
    help="Agent to start (default: all)",
)
@click.option(
    "--detach",
    is_flag=True,
    help="Run in background (not yet implemented)",
)
def start_server(agent: str, detach: bool):
    """Start A2A server(s) for agent communication."""
    if detach:
        console.print(
            "[yellow]Warning: --detach flag not yet implemented. Running in foreground.[/yellow]"
        )

    async def _start():
        try:
            if agent == "all":
                console.print("[cyan]Starting all A2A agent servers...[/cyan]")
                servers = await start_all_agent_servers()
                console.print(f"[green]Started {len(servers)} agent servers[/green]")

                # Keep servers running
                console.print(
                    "\n[yellow]Servers running. Press Ctrl+C to stop.[/yellow]\n"
                )
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    console.print("\n[cyan]Stopping all servers...[/cyan]")
                    from arl.a2a.server import stop_all_agent_servers
                    await stop_all_agent_servers(servers)
                    console.print("[green]All servers stopped[/green]")

            else:
                # Start single agent server
                console.print(f"[cyan]Starting A2A server for {agent}...[/cyan]")

                # Import the appropriate agent factory
                agent_factories = {
                    "hypothesis": "arl.adk_agents.hypothesis.agent:create_hypothesis_agent",
                    "experiment": "arl.adk_agents.experiment.agent:create_experiment_designer",
                    "code_gen": "arl.adk_agents.code_gen.agent:create_code_generator",
                    "execution": "arl.adk_agents.execution.agent:create_execution_engine",
                    "analysis": "arl.adk_agents.analysis.agent:create_analysis_agent",
                }

                # Dynamically import and create agent
                module_path, func_name = agent_factories[agent].split(":")
                module = __import__(module_path, fromlist=[func_name])
                factory_func = getattr(module, func_name)
                agent_instance = factory_func()

                # Create and start server
                server = create_a2a_server(agent_instance, agent)
                await server.serve_forever()

        except Exception as e:
            console.print(f"[red]Error starting A2A server: {e}[/red]")
            logger.error(f"A2A server error: {e}", exc_info=True)
            raise

    asyncio.run(_start())


@a2a_cli.command(name="test")
@click.option(
    "--agent",
    type=click.Choice(["hypothesis", "experiment", "code_gen", "execution", "analysis"]),
    required=True,
    help="Agent to test",
)
@click.option(
    "--url",
    type=str,
    help="Agent URL (default: local URL from config)",
)
def test_connection(agent: str, url: str | None):
    """Test connection to an A2A agent."""
    from arl.a2a.client import A2AAgentClient

    async def _test():
        try:
            console.print(f"[cyan]Testing connection to {agent} agent...[/cyan]")

            # Create client
            client = A2AAgentClient(agent, service_url=url)
            await client.initialize()

            # Get agent card
            agent_card = await client.get_agent_card()

            console.print(f"[green]✓ Successfully connected to {agent}[/green]")
            console.print("\n[bold]Agent Card:[/bold]")
            console.print(f"Name: {agent_card.get('name')}")
            console.print(f"Display Name: {agent_card.get('display_name')}")
            console.print(f"Description: {agent_card.get('description')}")
            console.print(f"Version: {agent_card.get('version')}")
            console.print(f"Protocol Version: {agent_card.get('protocol_version')}")

            # Close client
            await client.close()

        except Exception as e:
            console.print(f"[red]✗ Connection failed: {e}[/red]")
            logger.error(f"Connection test failed: {e}", exc_info=True)
            raise click.Abort()

    asyncio.run(_test())


@a2a_cli.command(name="enable")
def enable_a2a():
    """Enable A2A protocol for agent communication."""
    console.print(
        "[yellow]To enable A2A protocol, set ARL_A2A_ENABLED=true in your .env file[/yellow]"
    )
    console.print("\nExample:")
    console.print("  echo 'ARL_A2A_ENABLED=true' >> .env")
    console.print("  echo 'ARL_A2A_DEPLOYMENT_MODE=remote' >> .env")


@a2a_cli.command(name="disable")
def disable_a2a():
    """Disable A2A protocol (use local agent communication)."""
    console.print(
        "[yellow]To disable A2A protocol, set ARL_A2A_ENABLED=false in your .env file[/yellow]"
    )
    console.print("\nExample:")
    console.print("  echo 'ARL_A2A_ENABLED=false' >> .env")


# Register with main CLI
def register_with_cli(cli_group):
    """Register A2A commands with the main CLI."""
    cli_group.add_command(a2a_cli)
