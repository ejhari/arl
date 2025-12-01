#!/usr/bin/env python
"""
Example 2: Paper Library Management

This example demonstrates:
1. Creating a project
2. Searching arXiv for papers
3. Ingesting papers into the library
4. Viewing paper details
5. Searching the local library

Run: python examples/example_02_paper_ingestion.py
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from arl.core.project.project_service import ProjectService
from arl.core.knowledge.paper_service import PaperService
from arl.integrations.papers.arxiv_client import ArxivClient
from arl.storage.database import init_db
from arl.storage.models import DomainType

console = Console()


def main():
    """Run paper ingestion example."""
    console.print("\n[bold cyan]ARL Paper Library Example[/bold cyan]\n")

    # Initialize
    console.print("[bold]Initializing...[/bold]")
    init_db()
    console.print("[green]✓[/green] Database initialized\n")

    # Create project
    console.print("[bold]Step 1:[/bold] Creating project...")
    project_service = ProjectService()
    project = project_service.create_project(
        name="Machine Learning Research",
        domain=DomainType.CS,
    )
    console.print(f"[green]✓[/green] Project: {project.name}\n")

    # Search arXiv
    console.print("[bold]Step 2:[/bold] Searching arXiv for papers...")
    console.print("[dim](Searching for 'adversarial training' papers)[/dim]\n")

    try:
        arxiv_client = ArxivClient()
        papers = arxiv_client.search_papers(
            query="adversarial training neural networks",
            max_results=5,
        )

        console.print(f"[green]✓[/green] Found {len(papers)} papers on arXiv\n")

        # Display search results
        table = Table(title="arXiv Search Results")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Authors", style="yellow")
        table.add_column("Year", style="blue")

        for paper in papers[:3]:  # Show first 3
            authors = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors += f" (+{len(paper.authors) - 2})"

            table.add_row(
                paper.arxiv_id[:12],
                paper.title[:60] + "..." if len(paper.title) > 60 else paper.title,
                authors[:30],
                paper.published[:4],
            )

        console.print(table)
        console.print()

        # Ingest first paper
        if papers:
            console.print("[bold]Step 3:[/bold] Ingesting paper into library...")
            paper_to_ingest = papers[0]
            console.print(f"[dim]Ingesting: {paper_to_ingest.title[:60]}...[/dim]\n")

            paper_service = PaperService()

            try:
                ingested_paper = paper_service.ingest_from_arxiv(
                    project_id=project.project_id,
                    arxiv_id=paper_to_ingest.arxiv_id,
                )

                console.print("[green]✓[/green] Paper ingested successfully!\n")

                # Display paper details
                console.print(Panel(
                    f"[bold]Title:[/bold] {ingested_paper.title}\n\n"
                    f"[bold]Authors:[/bold] {', '.join(ingested_paper.authors[:3])}"
                    f"{' (+' + str(len(ingested_paper.authors) - 3) + ')' if len(ingested_paper.authors) > 3 else ''}\n\n"
                    f"[bold]Year:[/bold] {ingested_paper.year}\n\n"
                    f"[bold]PDF:[/bold] {ingested_paper.pdf_path}\n\n"
                    f"[bold]Pages:[/bold] {ingested_paper.extracted_knowledge.get('num_pages', 'N/A') if ingested_paper.extracted_knowledge else 'N/A'}\n\n"
                    f"[bold]Sections:[/bold] {len(ingested_paper.extracted_knowledge.get('sections', {})) if ingested_paper.extracted_knowledge else 0}",
                    title="Ingested Paper Details",
                    border_style="green",
                ))

                # Show abstract
                if ingested_paper.paper_metadata and "abstract" in ingested_paper.paper_metadata:
                    abstract = ingested_paper.paper_metadata["abstract"]
                    console.print("\n[bold]Abstract:[/bold]")
                    console.print(f"[dim]{abstract[:400]}...[/dim]\n")

                # List papers in library
                console.print("[bold]Step 4:[/bold] Listing papers in library...")
                papers_in_lib = paper_service.list_papers(project.project_id)
                console.print(f"[green]✓[/green] Library contains {len(papers_in_lib)} paper(s)\n")

                # Search library
                console.print("[bold]Step 5:[/bold] Searching local library...")
                search_results = paper_service.search_papers(
                    project.project_id,
                    "adversarial",
                )
                console.print(f"[green]✓[/green] Found {len(search_results)} matching papers\n")

            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not ingest paper: {e}")
                console.print("[dim]PDF download might have failed or taken too long[/dim]\n")

    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Could not search arXiv: {e}")
        console.print("[dim]Network connection required for arXiv search[/dim]\n")

    # Next steps
    console.print("[bold]Next Steps:[/bold]")
    console.print("  1. Ingest more papers:")
    console.print(f"     [cyan]arl paper ingest --project {project.project_id} --arxiv <arxiv-id>[/cyan]")
    console.print("  2. Search library:")
    console.print(f"     [cyan]arl paper search --project {project.project_id} 'your query'[/cyan]")
    console.print("  3. Use papers for research:")
    console.print(f"     [cyan]arl research start --project {project.project_id} --request 'your hypothesis'[/cyan]")
    console.print("\n[green]Paper library example complete![/green]\n")


if __name__ == "__main__":
    main()
