"""Session management service."""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session as DBSession

from arl.storage.database import get_db
from arl.storage.models import Session, SessionStatus


class SessionService:
    """Service for managing research sessions."""

    def __init__(self, db: DBSession | None = None):
        """Initialize service."""
        self.db = db or next(get_db())

    def create_session(self, project_id: str) -> Session:
        """Create new research session."""
        session = Session(
            project_id=project_id,
            status=SessionStatus.ACTIVE,
            state={},
            events=[],
            checkpoints=[],
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_session(self, session_id: str) -> Session | None:
        """Get session by ID."""
        return self.db.query(Session).filter(Session.session_id == session_id).first()

    def update_state(self, session_id: str, state: dict[str, Any]) -> Session:
        """Update session state by merging new state with existing state."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Merge new state with existing state (new values override old ones)
        current_state = session.state or {}
        merged_state = {**current_state, **state}
        session.state = merged_state
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    def add_event(self, session_id: str, event: dict[str, Any]) -> Session:
        """Add event to session log."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        events = session.events or []
        events.append({**event, "timestamp": datetime.utcnow().isoformat()})
        session.events = events
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    def create_checkpoint(self, session_id: str, name: str) -> Session:
        """Create session checkpoint."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        checkpoints = session.checkpoints or []
        checkpoints.append({
            "name": name,
            "state": session.state,
            "timestamp": datetime.utcnow().isoformat(),
        })
        session.checkpoints = checkpoints
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    def complete_session(self, session_id: str) -> Session:
        """Mark session as completed."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.status = SessionStatus.COMPLETED
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    def list_sessions(self, project_id: str) -> list[Session]:
        """List all sessions for project."""
        return (
            self.db.query(Session)
            .filter(Session.project_id == project_id)
            .order_by(Session.created_at.desc())
            .all()
        )
