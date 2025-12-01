#!/usr/bin/env python
"""Test dynamic dependency installation with uv."""

import asyncio
from arl.adk_agents.execution.agent import create_execution_engine
from rich.console import Console

console = Console()


async def test_dynamic_dependencies():
    """Test dynamic dependency installation."""
    console.print("[bold cyan]Testing Dynamic Dependency Installation with uv[/bold cyan]\n")

    # Test code that uses packages NOT in base image
    test_code = '''
import requests
from bs4 import BeautifulSoup
import yaml

print("Testing dynamic dependencies...")
print(f"requests version: {requests.__version__}")
print(f"beautifulsoup4 installed: {BeautifulSoup is not None}")
print(f"pyyaml installed: {yaml is not None}")

# Test functionality
response_mock = type('Response', (), {'status_code': 200, 'text': '<html><body><h1>Test</h1></body></html>'})()
soup = BeautifulSoup(response_mock.text, 'html.parser')
print(f"Parsed HTML title: {soup.find('h1').text}")

# Test YAML
data = {'test': 'value', 'number': 42}
yaml_str = yaml.dump(data)
print(f"YAML output: {yaml_str.strip()}")

print("All dynamic dependencies working!")
'''

    console.print("[bold]Test Code (requires: requests, beautifulsoup4, pyyaml):[/bold]")
    console.print("[dim]These packages are NOT in the base image[/dim]\n")

    try:
        console.print("[yellow]Executing with dynamic dependency installation...[/yellow]\n")

        execution_engine = create_execution_engine()
        result = await execution_engine.run(
            experiment_id="test_dynamic_deps",
            code=test_code,
            dependencies=["requests>=2.28.0", "beautifulsoup4>=4.11.0", "pyyaml>=6.0"],
            timeout_seconds=120,
        )

        console.print(f"[bold]Success:[/bold] {result['success']}")
        console.print(f"[bold]Exit Code:[/bold] {result['exit_code']}")
        console.print()

        if result['stdout']:
            console.print("[bold green]Output:[/bold green]")
            console.print(result['stdout'])
            console.print()

        if result['stderr']:
            console.print("[bold yellow]Errors/Warnings:[/bold yellow]")
            console.print(result['stderr'])
            console.print()

        if result['success']:
            console.print("\n[bold green]✓ Dynamic dependency installation with uv working![/bold green]")
            console.print("[dim]Packages were installed at runtime and code executed successfully[/dim]")
        else:
            console.print("\n[bold red]✗ Execution failed[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_dynamic_dependencies())
