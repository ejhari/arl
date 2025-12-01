"""Paper management CLI commands."""

import click
from rich.console import Console
from rich.table import Table

from arl.core.knowledge import PaperService

console = Console()


@click.group(name="paper")
def paper_group() -> None:
    """Manage research papers."""
    pass


@paper_group.command(name="ingest")
@click.option("--project", "project_id", required=True, help="Project ID")
@click.option("--arxiv", "arxiv_id", required=True, help="arXiv paper ID (e.g., 2301.00001)")
def ingest_paper(project_id: str, arxiv_id: str) -> None:
    """Ingest a paper from arXiv into project library."""
    console.print(f"[cyan]Ingesting paper {arxiv_id} from arXiv...[/cyan]")

    try:
        service = PaperService()
        paper = service.ingest_from_arxiv(project_id, arxiv_id)

        console.print(f"[bold green]✓[/bold green] Paper ingested: {paper.paper_id}")
        console.print(f"  Title: {paper.title}")
        console.print(f"  Authors: {', '.join(paper.authors[:3])}")
        if len(paper.authors) > 3:
            console.print(f"           (+{len(paper.authors) - 3} more)")
        console.print(f"  Year: {paper.year}")
        console.print(f"  PDF: {paper.pdf_path}")

        if paper.extracted_knowledge:
            num_pages = paper.extracted_knowledge.get("num_pages", "unknown")
            sections = paper.extracted_knowledge.get("sections", {})
            console.print(f"  Pages: {num_pages}")
            console.print(f"  Sections extracted: {len(sections)}")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to ingest paper: {e}")


@paper_group.command(name="list")
@click.option("--project", "project_id", required=True, help="Project ID")
def list_papers(project_id: str) -> None:
    """List all papers in project library."""
    service = PaperService()
    papers = service.list_papers(project_id)

    if not papers:
        console.print("[yellow]No papers found in project library[/yellow]")
        return

    table = Table(title=f"Papers in Project")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Authors", style="magenta")
    table.add_column("Year", style="blue")
    table.add_column("Source", style="yellow")

    for paper in papers:
        authors_str = ", ".join(paper.authors[:2])
        if len(paper.authors) > 2:
            authors_str += f" (+{len(paper.authors) - 2})"

        table.add_row(
            paper.paper_id[:8] + "...",
            paper.title[:50] + ("..." if len(paper.title) > 50 else ""),
            authors_str,
            paper.year or "N/A",
            paper.source.value,
        )

    console.print(table)
    console.print(f"\n[bold]Total papers: {len(papers)}[/bold]")


@paper_group.command(name="show")
@click.argument("paper_id")
def show_paper(paper_id: str) -> None:
    """Show paper details."""
    service = PaperService()
    paper = service.get_paper(paper_id)

    if not paper:
        console.print(f"[red]✗[/red] Paper not found: {paper_id}")
        return

    console.print(f"[bold]Paper Details[/bold]")
    console.print(f"  ID: {paper.paper_id}")
    console.print(f"  Title: {paper.title}")
    console.print(f"  Authors: {', '.join(paper.authors)}")
    console.print(f"  Year: {paper.year}")
    console.print(f"  Source: {paper.source.value}")

    if paper.arxiv_id:
        console.print(f"  arXiv ID: {paper.arxiv_id}")

    if paper.doi:
        console.print(f"  DOI: {paper.doi}")

    if paper.pdf_path:
        console.print(f"  PDF: {paper.pdf_path}")

    if paper.paper_metadata:
        console.print(f"\n[bold]Metadata:[/bold]")
        if "abstract" in paper.paper_metadata:
            abstract = paper.paper_metadata["abstract"]
            console.print(f"  Abstract: {abstract[:200]}...")
        if "categories" in paper.paper_metadata:
            console.print(f"  Categories: {', '.join(paper.paper_metadata['categories'])}")

    if paper.extracted_knowledge:
        console.print(f"\n[bold]Extracted Knowledge:[/bold]")
        num_pages = paper.extracted_knowledge.get("num_pages", "unknown")
        console.print(f"  Pages: {num_pages}")

        sections = paper.extracted_knowledge.get("sections", {})
        if sections:
            console.print(f"  Sections: {', '.join(sections.keys())}")


@paper_group.command(name="search")
@click.option("--project", "project_id", required=True, help="Project ID")
@click.argument("query")
def search_papers(project_id: str, query: str) -> None:
    """Search papers in project library."""
    service = PaperService()
    papers = service.search_papers(project_id, query)

    if not papers:
        console.print(f"[yellow]No papers found matching '{query}'[/yellow]")
        return

    console.print(f"[bold]Found {len(papers)} papers matching '{query}':[/bold]\n")

    for paper in papers:
        console.print(f"[cyan]{paper.paper_id[:8]}...[/cyan] {paper.title}")
        console.print(f"  Authors: {', '.join(paper.authors[:3])}")
        console.print(f"  Year: {paper.year}\n")
