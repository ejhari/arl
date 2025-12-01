"""PDF parsing and text extraction."""

from pathlib import Path
from typing import Any

import PyPDF2
from pydantic import BaseModel


class ExtractedContent(BaseModel):
    """Extracted content from PDF."""

    text: str
    num_pages: int
    sections: dict[str, str] = {}  # Section name -> content


class PDFParser:
    """Parse and extract text from PDF papers."""

    # Common section headers in academic papers
    SECTION_HEADERS = [
        "abstract",
        "introduction",
        "background",
        "related work",
        "methodology",
        "methods",
        "approach",
        "experiments",
        "results",
        "discussion",
        "conclusion",
        "references",
    ]

    def extract_text(self, pdf_path: Path) -> ExtractedContent:
        """
        Extract text from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted content with text and sections
        """
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)

            # Extract all text
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"

            # Attempt to identify sections
            sections = self._identify_sections(full_text)

            return ExtractedContent(
                text=full_text,
                num_pages=num_pages,
                sections=sections,
            )

    def _identify_sections(self, text: str) -> dict[str, str]:
        """
        Identify and extract paper sections.

        This is a simplified approach. More sophisticated parsing
        would use ML models or layout analysis.
        """
        sections = {}
        lines = text.split("\n")

        current_section = "preamble"
        section_content = []

        for line in lines:
            line_lower = line.lower().strip()

            # Check if line is a section header
            matched_header = None
            for header in self.SECTION_HEADERS:
                if line_lower == header or line_lower.startswith(header):
                    matched_header = header
                    break

            if matched_header:
                # Save previous section
                if section_content:
                    sections[current_section] = "\n".join(section_content)

                # Start new section
                current_section = matched_header
                section_content = []
            else:
                section_content.append(line)

        # Save last section
        if section_content:
            sections[current_section] = "\n".join(section_content)

        return sections
