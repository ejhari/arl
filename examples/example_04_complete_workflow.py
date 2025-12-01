#!/usr/bin/env python
"""
Example 4: Complete Research Workflow

This example demonstrates a full end-to-end research cycle:
1. Project and session setup
2. Hypothesis generation
3. Experiment design
4. Code generation and validation
5. Execution (simulated - requires Docker)
6. Result analysis

Run: python examples/example_04_complete_workflow.py
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from arl.adk_agents.hypothesis.agent import create_hypothesis_agent
from arl.adk_agents.experiment.agent import create_experiment_designer
from arl.adk_agents.code_gen.agent import create_code_generator
from arl.adk_agents.execution.agent import create_execution_engine
from arl.adk_agents.analysis.agent import create_analysis_agent
from arl.core.project.project_service import ProjectService
from arl.core.session.session_service import SessionService
from arl.core.memory.memory_service import MemoryService
from arl.storage.database import init_db
from arl.storage.models import DomainType
from arl.config.settings import settings

console = Console()


async def run_complete_workflow():
    """Run complete research workflow."""
    console.print("\n[bold cyan]ARL Complete Research Workflow Example[/bold cyan]\n")

    # Setup
    console.print("[bold]Setup Phase[/bold]\n")
    init_db()

    project_service = ProjectService()
    project = project_service.create_project(
        name="ML Algorithm Comparison Study",
        domain=DomainType.CS,
        objectives="Compare machine learning algorithms on classification tasks",
    )

    session_service = SessionService()
    session = session_service.create_session(project.project_id)
    memory_service = MemoryService()

    console.print(f"[green]✓[/green] Project: {project.name}")
    console.print(f"[green]✓[/green] Session: {session.session_id[:8]}...\n")

    # Stage 1: Hypothesis Generation
    console.print("[bold cyan]Stage 1: Hypothesis Generation[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating hypotheses...", total=None)

        hypotheses = await create_hypothesis_agent().run(
            literature_summary="""
Random forests and gradient boosting are popular ensemble methods.
Recent studies suggest XGBoost performs well on tabular data.
However, systematic comparisons across diverse datasets are limited.
            """.strip(),
            research_gap="Lack of comprehensive comparison of ensemble methods on diverse datasets",
            domain="cs",
        )

        progress.update(task, completed=True)

    memory_service.store_memory(session.session_id, "hypotheses", hypotheses)

    console.print("\n[green]✓[/green] Hypotheses Generated\n")
    console.print(Panel(
        hypotheses["raw_output"][:500] + "..." if len(hypotheses["raw_output"]) > 500 else hypotheses["raw_output"],
        title="Generated Hypotheses",
        border_style="cyan",
    ))
    console.print(f"\n[dim]Tokens: {hypotheses['tokens_used']}[/dim]\n")

    # Stage 2: Experiment Design
    console.print("\n[bold cyan]Stage 2: Experiment Design[/bold cyan]\n")

    # Extract first hypothesis (simplified)
    hypothesis = "XGBoost will outperform Random Forest on classification tasks"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Designing experiment...", total=None)

        design = await create_experiment_designer().run(
            hypothesis=hypothesis,
            domain="cs",
            constraints={"max_training_time": "10 minutes", "datasets": "public"},
        )

        progress.update(task, completed=True)

    memory_service.store_memory(session.session_id, "design", design)

    console.print("\n[green]✓[/green] Experiment Designed\n")
    console.print(Panel(
        design["protocol"][:500] + "..." if len(design["protocol"]) > 500 else design["protocol"],
        title="Experimental Protocol",
        border_style="green",
    ))
    console.print()

    # Stage 3: Code Generation
    console.print("\n[bold cyan]Stage 3: Code Generation[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating Python code...", total=None)

        code_result = await create_code_generator().run(
            experiment_design=design,
            domain="cs",
        )

        progress.update(task, completed=True)

    memory_service.store_memory(session.session_id, "code", code_result)

    console.print("\n[green]✓[/green] Code Generated\n")
    console.print(f"[bold]Generated Code:[/bold]")
    console.print(f"  Length: {len(code_result['code'])} characters")
    console.print(f"  Valid: [{'green' if code_result['validation']['valid'] else 'red'}]{code_result['validation']['valid']}[/]")
    console.print(f"  Errors: {len(code_result['validation']['errors'])}")
    console.print(f"  Warnings: {len(code_result['validation']['warnings'])}")
    console.print(f"  Dependencies: {', '.join(code_result['dependencies'])}\n")

    # Show code snippet
    code_lines = code_result['code'].split('\n')[:30]
    console.print(Panel(
        '\n'.join(code_lines) + "\n\n[dim]... (truncated)[/dim]",
        title="Generated Code (first 30 lines)",
        border_style="blue",
    ))
    console.print()

    # Stage 4: Code Execution (using Docker)
    console.print("\n[bold cyan]Stage 4: Code Execution[/bold cyan]\n")

    execution_results = None
    if settings.docker_enabled:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Executing code in Docker sandbox...", total=None)

                execution_engine = create_execution_engine()
                execution_results = await execution_engine.run(
                    experiment_id=session.session_id,
                    code=code_result['code'],
                    timeout_seconds=600,  # 10 minutes for complex experiments
                )

                progress.update(task, completed=True)

            console.print(f"\n[green]✓[/green] Execution {'Successful' if execution_results['success'] else 'Failed'}\n")
            console.print(Panel(
                execution_results['stdout'] if execution_results['stdout'] else "[dim]No output[/dim]",
                title="Execution Output",
                border_style="green" if execution_results['success'] else "red",
            ))
            if execution_results['stderr']:
                console.print(Panel(
                    execution_results['stderr'],
                    title="Errors/Warnings",
                    border_style="yellow",
                ))
            console.print(f"\n[dim]Artifacts: {len(execution_results['artifacts'])}[/dim]")
            console.print()
        except Exception as e:
            console.print(f"[yellow]Warning: Docker execution failed: {e}[/yellow]")
            console.print("[dim]Falling back to simulated results...[/dim]\n")
            execution_results = None

    # Fallback to simulated results if Docker execution didn't work
    if execution_results is None:
        console.print("[dim](Using simulated execution results - Docker unavailable)[/dim]\n")
        execution_results = {
            "success": True,
            "stdout": """
Training Random Forest...
Random Forest - Accuracy: 0.87, Precision: 0.85, Recall: 0.88

Training XGBoost...
XGBoost - Accuracy: 0.91, Precision: 0.90, Recall: 0.92

Statistical Test: t-test p-value = 0.023
Effect Size (Cohen's d): 0.67
            """.strip(),
            "artifacts": ["results_plot.png", "metrics.csv"],
        }

    # Stage 5: Result Analysis
    console.print("\n[bold cyan]Stage 5: Result Analysis[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing results...", total=None)

        analysis = await create_analysis_agent().run(
            hypothesis=hypothesis,
            experiment_design=design,
            execution_results=execution_results,
            domain="cs",
        )

        progress.update(task, completed=True)

    console.print("\n[green]✓[/green] Analysis Complete\n")
    console.print(Panel(
        analysis["raw_analysis"][:600] + "..." if len(analysis["raw_analysis"]) > 600 else analysis["raw_analysis"],
        title="Statistical Analysis & Hypothesis Validation",
        border_style="magenta",
    ))
    console.print()

    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold green]RESEARCH CYCLE COMPLETE[/bold green]")
    console.print("=" * 60 + "\n")

    console.print("[bold]Summary:[/bold]")
    console.print(f"  Project: {project.name}")
    console.print(f"  Session: {session.session_id[:16]}...")
    console.print(f"  Hypothesis: {hypothesis}")
    console.print(f"  Code Generated: {len(code_result['code'])} chars")
    console.print(f"  Code Valid: {'Yes' if code_result['validation']['valid'] else 'No'}")
    console.print(f"  Dependencies: {len(code_result['dependencies'])}")
    console.print()

    console.print("[bold]Next Steps:[/bold]")
    console.print("  1. Review generated code in session memory")
    console.print("  2. Review execution artifacts")
    console.print("  3. Iterate based on analysis recommendations")
    console.print("  4. Compare results across different hypotheses")
    console.print()

    console.print("[green]Complete workflow example finished![/green]\n")


def main():
    """Entry point."""
    try:
        asyncio.run(run_complete_workflow())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}\n")
        console.print("[dim]Make sure API keys are configured and dependencies are installed[/dim]\n")


if __name__ == "__main__":
    main()
