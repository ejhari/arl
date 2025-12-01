"""Paper library management service."""

from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from arl.config.settings import settings
from arl.integrations.papers.arxiv_client import ArxivClient, PaperMetadata
from arl.integrations.papers.pdf_parser import PDFParser
from arl.storage.database import get_db
from arl.storage.models import Paper, PaperSource


class PaperService:
    """Service for managing paper library."""

    def __init__(self, db: Session | None = None):
        """Initialize service."""
        self.db = db or next(get_db())
        self.arxiv_client = ArxivClient()
        self.pdf_parser = PDFParser()

    def ingest_from_arxiv(
        self,
        project_id: str,
        arxiv_id: str,
    ) -> Paper:
        """
        Ingest paper from arXiv.

        Args:
            project_id: Project to add paper to
            arxiv_id: arXiv paper ID

        Returns:
            Created Paper object
        """
        # Get metadata
        metadata = self.arxiv_client.get_paper_by_id(arxiv_id)
        if not metadata:
            raise ValueError(f"Paper not found: {arxiv_id}")

        # Download PDF
        pdf_dir = settings.data_dir / "papers" / project_id
        pdf_path = self.arxiv_client.download_pdf(arxiv_id, pdf_dir)

        # Extract text
        content = self.pdf_parser.extract_text(pdf_path)

        # Create paper record
        paper = Paper(
            project_id=project_id,
            title=metadata.title,
            authors=metadata.authors,
            year=metadata.published[:4],
            arxiv_id=arxiv_id,
            source=PaperSource.ARXIV,
            pdf_path=str(pdf_path),
            paper_metadata={
                "abstract": metadata.abstract,
                "categories": metadata.categories,
                "published": metadata.published,
                "updated": metadata.updated,
            },
            extracted_knowledge={
                "full_text": content.text,
                "sections": content.sections,
                "num_pages": content.num_pages,
            },
        )

        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)

        return paper

    def search_papers(
        self,
        project_id: str,
        query: str,
    ) -> list[Paper]:
        """
        Search papers in project library.

        Args:
            project_id: Project ID
            query: Search query (simple text match for now)

        Returns:
            List of matching papers
        """
        papers = (
            self.db.query(Paper)
            .filter(Paper.project_id == project_id)
            .filter(Paper.title.contains(query))
            .all()
        )
        return papers

    def get_paper(self, paper_id: str) -> Paper | None:
        """Get paper by ID."""
        return self.db.query(Paper).filter(Paper.paper_id == paper_id).first()

    def list_papers(self, project_id: str) -> list[Paper]:
        """List all papers in project."""
        return self.db.query(Paper).filter(Paper.project_id == project_id).all()
