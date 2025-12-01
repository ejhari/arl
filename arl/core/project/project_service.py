"""Project management service."""

from sqlalchemy.orm import Session as DBSession

from arl.storage.database import get_db
from arl.storage.models import DomainType, Project


class ProjectService:
    """Service for managing research projects."""

    def __init__(self, db: DBSession | None = None):
        """Initialize service."""
        self.db = db or next(get_db())

    def create_project(
        self,
        name: str,
        domain: DomainType | str,
        objectives: str | None = None,
        constraints: dict | None = None,
    ) -> Project:
        """Create new research project."""
        if isinstance(domain, str):
            domain = DomainType(domain)

        project = Project(
            name=name,
            domain=domain,
            objectives=objectives,
            constraints=constraints,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def get_project(self, project_id: str) -> Project | None:
        """Get project by ID."""
        return self.db.query(Project).filter(Project.project_id == project_id).first()

    def list_projects(self) -> list[Project]:
        """List all projects."""
        return self.db.query(Project).order_by(Project.created_at.desc()).all()
