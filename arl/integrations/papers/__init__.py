"""Paper ingestion and processing integrations."""

from arl.integrations.papers.arxiv_client import ArxivClient, PaperMetadata
from arl.integrations.papers.pdf_parser import ExtractedContent, PDFParser

__all__ = ["ArxivClient", "PaperMetadata", "PDFParser", "ExtractedContent"]
