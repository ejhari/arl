#!/usr/bin/env python
"""
Example 1: Quick Start with ARL

This example demonstrates the basic workflow:
1. Create a project
2. Start a research session
3. Generate hypotheses
4. View results

Run: python examples/example_01_quick_start.py
"""

import asyncio
from rich.console import Console
from rich.panel import Panel

from arl.core.project.project_service import ProjectService
from arl.core.session.session_service import SessionService
from arl.adk_agents.hypothesis.agent import create_hypothesis_agent
from arl.storage.database import init_db
from arl.storage.models import DomainType

console = Console()


def main():
    """Run quick start example."""
    console.print("\n[bold cyan]ARL Quick Start Example[/bold cyan]\n")

    # Step 1: Initialize database
    console.print("[bold]Step 1:[/bold] Initializing database...")
    init_db()
    console.print("[green]✓[/green] Database initialized\n")

    # Step 2: Create a project
    console.print("[bold]Step 2:[/bold] Creating research project...")
    project_service = ProjectService()
    project = project_service.create_project(
        name="Neural Network Robustness Study",
        domain=DomainType.CS,
        objectives="Investigate techniques for improving neural network robustness to adversarial examples",
    )
    console.print(f"[green]✓[/green] Project created: {project.project_id[:8]}...")
    console.print(f"  Name: {project.name}")
    console.print(f"  Domain: {project.domain.value}\n")

    # Step 3: Create a research session
    console.print("[bold]Step 3:[/bold] Starting research session...")
    session_service = SessionService()
    session = session_service.create_session(project.project_id)
    console.print(f"[green]✓[/green] Session created: {session.session_id[:8]}...")
    console.print(f"  Status: {session.status.value}\n")

    # Step 4: Generate hypotheses
    console.print("[bold]Step 4:[/bold] Generating research hypotheses...")
    console.print("[dim](This uses the LLM to generate hypotheses - requires API key)[/dim]\n")

    async def generate_hypotheses():
        agent = create_hypothesis_agent()

        result = await agent.run(
            literature_summary="""
Recent research shows that neural networks are vulnerable to adversarial examples -
small perturbations that cause misclassification. Several defense techniques have been
proposed including adversarial training, certified defenses, and input transformations.
However, there's limited systematic comparison across domains and architectures.
            """.strip(),
            research_gap="Lack of comprehensive comparison of robustness techniques across different domains and model architectures",
            domain="cs",
        )

        return result

    # Run async hypothesis generation
    try:
        result = asyncio.run(generate_hypotheses())

        console.print("[green]✓[/green] Hypotheses generated!\n")

        # Display results
        console.print(Panel(
            result["raw_output"][:800] + "..." if len(result["raw_output"]) > 800 else result["raw_output"],
            title="Generated Hypotheses",
            border_style="cyan",
        ))

        console.print(f"\n[dim]Model used: {result['model_used']}[/dim]")
        console.print(f"[dim]Tokens: {result['tokens_used']}[/dim]\n")

    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Could not generate hypotheses: {e}")
        console.print("[dim]Make sure you have set GOOGLE_API_KEY, AZURE_OPENAI_API_KEY, or ANTHROPIC_API_KEY[/dim]\n")

    # Step 5: Next steps
    console.print("[bold]Next Steps:[/bold]")
    console.print("  1. Continue with experiment design:")
    console.print(f"     [cyan]arl research continue --session {session.session_id}[/cyan]")
    console.print("  2. Or run complete workflow:")
    console.print(f"     [cyan]arl research run --project {project.project_id} --request 'your hypothesis' --auto[/cyan]")
    console.print("\n[green]Quick start complete![/green]\n")


if __name__ == "__main__":
    main()
