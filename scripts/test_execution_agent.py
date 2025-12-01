#!/usr/bin/env python
"""Test the execution agent with Docker."""

import asyncio
from arl.adk_agents.execution.agent import create_execution_engine
from rich.console import Console

console = Console()


async def test_execution():
    """Test execution agent."""
    console.print("[bold cyan]Testing Execution Agent with Docker[/bold cyan]\n")

    # Simple test code
    test_code = '''
import numpy as np
import pandas as pd

print("Testing execution in Docker sandbox...")
print(f"NumPy version: {np.__version__}")
print(f"Pandas version: {pd.__version__}")

# Simple calculation
data = np.array([1, 2, 3, 4, 5])
mean = data.mean()
print(f"Mean of {data.tolist()}: {mean}")

# Create a simple DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})
print(f"DataFrame:\\n{df}")

# Save result
with open("result.txt", "w") as f:
    f.write(f"Mean: {mean}\\n")

print("Execution complete!")
'''

    console.print("[bold]Test Code:[/bold]")
    console.print(test_code)
    console.print()

    try:
        console.print("[yellow]Executing in Docker sandbox...[/yellow]\n")

        execution_engine = create_execution_engine()
        result = await execution_engine.run(
            experiment_id="test_execution",
            code=test_code,
            timeout_seconds=30,
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

        console.print(f"[bold]Artifacts:[/bold] {len(result['artifacts'])}")
        for artifact in result['artifacts']:
            console.print(f"  - {artifact}")

        if result['success']:
            console.print("\n[bold green]✓ Docker execution is working![/bold green]")
        else:
            console.print("\n[bold red]✗ Execution failed[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_execution())
