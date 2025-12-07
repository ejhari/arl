"""API Router"""

from fastapi import APIRouter
from app.api.endpoints import auth, projects, cells, documents, teams, permissions, exports, agents, sessions

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(cells.router, prefix="/cells", tags=["cells"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(permissions.router, prefix="", tags=["permissions"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(sessions.router, prefix="", tags=["sessions"])
