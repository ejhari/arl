"""Export service for generating exports"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from app.models.export import Export, ExportStatus
from app.models.cell import Cell


class ExportService:
    """Service for generating project exports"""

    def __init__(self, export_dir: str = "storage/exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def generate_export(
        self,
        export: Export,
        cells: List[Cell],
    ) -> str:
        """Generate export file based on format"""
        try:
            if export.format.value == "json":
                file_path = await self._generate_json(export, cells)
            elif export.format.value == "markdown":
                file_path = await self._generate_markdown(export, cells)
            elif export.format.value == "html":
                file_path = await self._generate_html(export, cells)
            elif export.format.value == "pdf":
                raise NotImplementedError("PDF export not yet implemented")
            else:
                raise ValueError(f"Unsupported export format: {export.format}")

            return file_path
        except Exception as e:
            raise Exception(f"Export generation failed: {str(e)}")

    async def _generate_json(self, export: Export, cells: List[Cell]) -> str:
        """Generate JSON export"""
        config = export.config or {}

        # Build export data
        export_data = {
            "project_id": export.project_id,
            "exported_at": datetime.utcnow().isoformat(),
            "format": "json",
            "cells": []
        }

        for cell in cells:
            cell_data = {
                "id": cell.id,
                "type": cell.cell_type,
                "position": cell.position,
                "created_at": cell.created_at.isoformat(),
            }

            # Include content based on config
            if config.get("include_code", True) or cell.cell_type != "code":
                cell_data["content"] = cell.content

            # Include outputs if configured
            if config.get("include_outputs", True) and cell.outputs:
                cell_data["outputs"] = [
                    {
                        "output_type": output.output_type,
                        "content": output.content,
                    }
                    for output in cell.outputs
                ]

            export_data["cells"].append(cell_data)

        # Write to file
        filename = f"{export.id}.json"
        file_path = self.export_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        return str(file_path)

    async def _generate_markdown(self, export: Export, cells: List[Cell]) -> str:
        """Generate Markdown export"""
        config = export.config or {}
        lines = []

        # Header
        lines.append(f"# Project Export")
        lines.append(f"\nExported at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")

        # Process cells
        for cell in cells:
            if cell.cell_type == "markdown":
                lines.append(f"\n{cell.content}\n")

            elif cell.cell_type == "code" and config.get("include_code", True):
                lines.append(f"\n## Code Cell\n")
                lines.append(f"```python\n{cell.content or ''}\n```\n")

                # Include outputs
                if config.get("include_outputs", True) and cell.outputs:
                    lines.append("\n**Output:**\n")
                    for output in cell.outputs:
                        if output.output_type == "stream":
                            lines.append(f"```\n{output.content}\n```\n")
                        elif output.output_type == "error":
                            lines.append(f"```\nError: {output.content}\n```\n")

            elif cell.cell_type == "visualization" and config.get("include_visualizations", True):
                lines.append(f"\n## Visualization\n")
                lines.append(f"\n*[Visualization data omitted in markdown export]*\n")

        # Write to file
        filename = f"{export.id}.md"
        file_path = self.export_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return str(file_path)

    async def _generate_html(self, export: Export, cells: List[Cell]) -> str:
        """Generate HTML export"""
        config = export.config or {}
        html_parts = []

        # HTML header
        html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Export</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        .header {
            border-bottom: 2px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .cell {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #eee;
            border-radius: 8px;
        }
        .cell-type {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        pre {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        code {
            font-family: 'Courier New', monospace;
        }
        .output {
            margin-top: 15px;
            padding: 10px;
            background: #f9f9f9;
            border-left: 3px solid #4CAF50;
        }
        .error {
            background: #ffebee;
            border-left-color: #f44336;
        }
    </style>
</head>
<body>
""")

        html_parts.append(f"""
    <div class="header">
        <h1>Project Export</h1>
        <p>Exported at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
""")

        # Process cells
        for cell in cells:
            if cell.cell_type == "markdown":
                html_parts.append(f"""
    <div class="cell">
        <div class="cell-type">Markdown</div>
        <div>{self._markdown_to_html(cell.content or '')}</div>
    </div>
""")

            elif cell.cell_type == "code" and config.get("include_code", True):
                html_parts.append(f"""
    <div class="cell">
        <div class="cell-type">Code</div>
        <pre><code>{self._escape_html(cell.content or '')}</code></pre>
""")

                # Include outputs
                if config.get("include_outputs", True) and cell.outputs:
                    for output in cell.outputs:
                        error_class = " error" if output.output_type == "error" else ""
                        html_parts.append(f"""
        <div class="output{error_class}">
            <strong>{'Error' if output.output_type == 'error' else 'Output'}:</strong>
            <pre><code>{self._escape_html(output.content or '')}</code></pre>
        </div>
""")

                html_parts.append("    </div>")

            elif cell.cell_type == "visualization" and config.get("include_visualizations", True):
                html_parts.append("""
    <div class="cell">
        <div class="cell-type">Visualization</div>
        <p><em>[Visualization data omitted in HTML export]</em></p>
    </div>
""")

        # HTML footer
        html_parts.append("""
</body>
</html>
""")

        # Write to file
        filename = f"{export.id}.html"
        file_path = self.export_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))

        return str(file_path)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    def _markdown_to_html(self, text: str) -> str:
        """Simple markdown to HTML conversion"""
        # Basic implementation - in production, use a proper markdown library
        html = self._escape_html(text)

        # Headers
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n', 1)
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)

        # Paragraphs
        lines = html.split('\n')
        html = '</p>\n<p>'.join(lines)
        html = f'<p>{html}</p>'

        return html


# Global instance
export_service = ExportService()
