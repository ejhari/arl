"""arXiv API client for paper retrieval."""

from pathlib import Path
from typing import Any

import arxiv
from pydantic import BaseModel

from arl.config.settings import settings


class PaperMetadata(BaseModel):
    """Paper metadata from arXiv."""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    published: str
    updated: str
    categories: list[str]
    pdf_url: str


class ArxivClient:
    """Client for arXiv API."""

    def __init__(self):
        """Initialize arXiv client."""
        self.client = arxiv.Client()

    def search_papers(
        self,
        query: str,
        max_results: int = 10,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
    ) -> list[PaperMetadata]:
        """
        Search arXiv for papers.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort_by: Sort criterion

        Returns:
            List of paper metadata
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
        )

        papers = []
        for result in self.client.results(search):
            papers.append(
                PaperMetadata(
                    arxiv_id=result.entry_id.split("/")[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    published=result.published.isoformat(),
                    updated=result.updated.isoformat(),
                    categories=result.categories,
                    pdf_url=result.pdf_url,
                )
            )

        return papers

    def get_paper_by_id(self, arxiv_id: str) -> PaperMetadata | None:
        """Get specific paper by arXiv ID."""
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(self.client.results(search))

        if not results:
            return None

        result = results[0]
        return PaperMetadata(
            arxiv_id=arxiv_id,
            title=result.title,
            authors=[author.name for author in result.authors],
            abstract=result.summary,
            published=result.published.isoformat(),
            updated=result.updated.isoformat(),
            categories=result.categories,
            pdf_url=result.pdf_url,
        )

    def download_pdf(self, arxiv_id: str, output_path: Path) -> Path:
        """
        Download PDF for paper.

        Args:
            arxiv_id: arXiv paper ID
            output_path: Directory to save PDF

        Returns:
            Path to downloaded PDF
        """
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(self.client.results(search))

        output_path.mkdir(parents=True, exist_ok=True)
        filename = f"{arxiv_id.replace('/', '_')}.pdf"
        pdf_path = output_path / filename

        paper.download_pdf(filename=str(pdf_path))

        return pdf_path
