"""Tests for export functionality"""

import pytest
from httpx import AsyncClient
from datetime import datetime
import os
import json

from app.models.export import Export, ExportStatus, ExportFormat
from app.models.project import Project
from app.models.cell import Cell
from app.models.user import User


class TestExportEndpoints:
    """Test export API endpoints"""

    @pytest.fixture
    async def test_user(self, db_session):
        """Create a test user"""
        from app.core.security import get_password_hash
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("testpass123"),
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def test_project(self, db_session, test_user):
        """Create a test project"""
        project = Project(
            name="Test Project",
            description="Test project for exports",
            owner_id=test_user.id,
            is_public=False,
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        return project

    @pytest.fixture
    async def test_cells(self, db_session, test_project, test_user):
        """Create test cells"""
        cells = [
            Cell(
                project_id=test_project.id,
                cell_type="markdown",
                content="# Test Notebook",
                position=0,
                created_by=test_user.id,
            ),
            Cell(
                project_id=test_project.id,
                cell_type="code",
                content="print('Hello World')",
                position=1,
                created_by=test_user.id,
            ),
        ]
        for cell in cells:
            db_session.add(cell)
        await db_session.commit()
        return cells

    @pytest.mark.asyncio
    async def test_create_export(self, client: AsyncClient, test_project, auth_headers):
        """Test creating an export job"""
        response = await client.post(
            "/api/v1/exports",
            headers=auth_headers,
            json={
                "project_id": test_project.id,
                "format": "json",
                "include_code": True,
                "include_outputs": True,
                "include_visualizations": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == test_project.id
        assert data["format"] == "json"
        assert data["status"] in ["pending", "processing", "completed"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_export_invalid_project(self, client: AsyncClient, auth_headers):
        """Test creating export for non-existent project"""
        response = await client.post(
            "/api/v1/exports",
            headers=auth_headers,
            json={
                "project_id": "00000000-0000-0000-0000-000000000000",
                "format": "json",
            },
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_export_status(self, client: AsyncClient, db_session, test_project, test_user, auth_headers):
        """Test getting export status"""
        # Create export
        export = Export(
            project_id=test_project.id,
            created_by=test_user.id,
            format=ExportFormat.JSON,
            status=ExportStatus.COMPLETED,
            file_path="/tmp/test_export.json",
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        # Get status
        response = await client.get(
            f"/api/v1/exports/{export.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == export.id
        assert data["status"] == "completed"
        assert data["format"] == "json"

    @pytest.mark.asyncio
    async def test_get_export_not_found(self, client: AsyncClient, auth_headers):
        """Test getting non-existent export"""
        response = await client.get(
            "/api/v1/exports/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_project_exports(self, client: AsyncClient, db_session, test_project, test_user, auth_headers):
        """Test listing exports for a project"""
        # Create multiple exports
        exports = [
            Export(
                project_id=test_project.id,
                created_by=test_user.id,
                format=ExportFormat.JSON,
                status=ExportStatus.COMPLETED,
            ),
            Export(
                project_id=test_project.id,
                created_by=test_user.id,
                format=ExportFormat.MARKDOWN,
                status=ExportStatus.PENDING,
            ),
        ]
        for export in exports:
            db_session.add(export)
        await db_session.commit()

        # List exports
        response = await client.get(
            f"/api/v1/exports?project_id={test_project.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(e["project_id"] == test_project.id for e in data)

    @pytest.mark.asyncio
    async def test_download_export(self, client: AsyncClient, db_session, test_project, test_user, auth_headers, tmp_path):
        """Test downloading a completed export"""
        # Create test export file
        export_file = tmp_path / "test_export.json"
        export_data = {"test": "data"}
        with open(export_file, "w") as f:
            json.dump(export_data, f)

        # Create export record
        export = Export(
            project_id=test_project.id,
            created_by=test_user.id,
            format=ExportFormat.JSON,
            status=ExportStatus.COMPLETED,
            file_path=str(export_file),
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        # Download export
        response = await client.get(
            f"/api/v1/exports/{export.id}/download",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_download_export_not_completed(self, client: AsyncClient, db_session, test_project, test_user, auth_headers):
        """Test downloading an incomplete export"""
        export = Export(
            project_id=test_project.id,
            created_by=test_user.id,
            format=ExportFormat.JSON,
            status=ExportStatus.PENDING,
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        response = await client.get(
            f"/api/v1/exports/{export.id}/download",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "pending" in response.json()["detail"].lower()


class TestExportService:
    """Test export service functionality"""

    @pytest.fixture
    def export_service(self, tmp_path):
        """Create export service with temp directory"""
        from app.services.export_service import ExportService
        return ExportService(export_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_generate_json_export(self, export_service, db_session, test_project, test_user, test_cells):
        """Test JSON export generation"""
        export = Export(
            project_id=test_project.id,
            created_by=test_user.id,
            format=ExportFormat.JSON,
            status=ExportStatus.PROCESSING,
            config={"include_code": True, "include_outputs": True},
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        # Generate export
        file_path = await export_service.generate_export(export, test_cells)

        # Verify file exists and content
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            data = json.load(f)

        assert data["project_id"] == test_project.id
        assert "cells" in data
        assert len(data["cells"]) == len(test_cells)

    @pytest.mark.asyncio
    async def test_generate_markdown_export(self, export_service, db_session, test_project, test_user, test_cells):
        """Test Markdown export generation"""
        export = Export(
            project_id=test_project.id,
            created_by=test_user.id,
            format=ExportFormat.MARKDOWN,
            status=ExportStatus.PROCESSING,
            config={"include_code": True},
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        # Generate export
        file_path = await export_service.generate_export(export, test_cells)

        # Verify file exists and content
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            content = f.read()

        assert "Test Notebook" in content
        assert "```python" in content
        assert "print('Hello World')" in content

    @pytest.mark.asyncio
    async def test_generate_html_export(self, export_service, db_session, test_project, test_user, test_cells):
        """Test HTML export generation"""
        export = Export(
            project_id=test_project.id,
            created_by=test_user.id,
            format=ExportFormat.HTML,
            status=ExportStatus.PROCESSING,
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        # Generate export
        file_path = await export_service.generate_export(export, test_cells)

        # Verify file exists and content
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            content = f.read()

        assert "<!DOCTYPE html>" in content
        assert "Test Notebook" in content
        assert "<code>" in content

    @pytest.mark.asyncio
    async def test_pdf_export_not_implemented(self, export_service, db_session, test_project, test_user, test_cells):
        """Test that PDF export raises NotImplementedError"""
        export = Export(
            project_id=test_project.id,
            created_by=test_user.id,
            format=ExportFormat.PDF,
            status=ExportStatus.PROCESSING,
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        with pytest.raises(NotImplementedError):
            await export_service.generate_export(export, test_cells)


class TestExportFormats:
    """Test different export formats"""

    @pytest.mark.asyncio
    async def test_export_with_code_excluded(self, export_service, db_session, test_project, test_user, test_cells):
        """Test export with code excluded"""
        export = Export(
            project_id=test_project.id,
            created_by=test_user.id,
            format=ExportFormat.JSON,
            status=ExportStatus.PROCESSING,
            config={"include_code": False},
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        file_path = await export_service.generate_export(export, test_cells)

        with open(file_path, "r") as f:
            data = json.load(f)

        # Markdown cell should be included, code cell content should be excluded
        assert len(data["cells"]) == len(test_cells)
        code_cells = [c for c in data["cells"] if c["type"] == "code"]
        assert all("content" not in c for c in code_cells)

    @pytest.mark.asyncio
    async def test_export_formats_enum(self):
        """Test export format enum values"""
        assert ExportFormat.JSON.value == "json"
        assert ExportFormat.MARKDOWN.value == "markdown"
        assert ExportFormat.HTML.value == "html"
        assert ExportFormat.PDF.value == "pdf"

    @pytest.mark.asyncio
    async def test_export_status_enum(self):
        """Test export status enum values"""
        assert ExportStatus.PENDING.value == "pending"
        assert ExportStatus.PROCESSING.value == "processing"
        assert ExportStatus.COMPLETED.value == "completed"
        assert ExportStatus.FAILED.value == "failed"


class TestExportPermissions:
    """Test export access control"""

    @pytest.mark.asyncio
    async def test_cannot_export_others_project(self, client: AsyncClient, db_session, auth_headers):
        """Test that users cannot export projects they don't own"""
        # Create another user's project
        other_user = User(
            email="other@example.com",
            full_name="Other User",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()

        project = Project(
            name="Other's Project",
            description="Not accessible",
            owner_id=other_user.id,
            is_public=False,
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Try to export
        response = await client.post(
            "/api/v1/exports",
            headers=auth_headers,
            json={
                "project_id": project.id,
                "format": "json",
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_cannot_access_others_export(self, client: AsyncClient, db_session, test_user, auth_headers):
        """Test that users cannot access exports created by others"""
        # Create another user and their export
        other_user = User(
            email="other@example.com",
            full_name="Other User",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()

        project = Project(
            name="Other's Project",
            description="Not accessible",
            owner_id=other_user.id,
        )
        db_session.add(project)
        await db_session.commit()

        export = Export(
            project_id=project.id,
            created_by=other_user.id,
            format=ExportFormat.JSON,
            status=ExportStatus.COMPLETED,
        )
        db_session.add(export)
        await db_session.commit()
        await db_session.refresh(export)

        # Try to access
        response = await client.get(
            f"/api/v1/exports/{export.id}",
            headers=auth_headers,
        )
        assert response.status_code == 403
