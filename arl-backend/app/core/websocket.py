"""WebSocket manager with Socket.IO"""

import socketio
import logging
from typing import Dict, Set, Optional
from app.core.redis import pubsub
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
    logger=True,
    engineio_logger=True,
)

# Create ASGI app for Socket.IO
socket_app = socketio.ASGIApp(sio)


class WebSocketManager:
    """Manages WebSocket connections and event broadcasting"""

    def __init__(self):
        self.active_connections: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        self.session_users: Dict[str, str] = {}  # session_id -> user_id

    async def connect(self, sid: str, user_id: str):
        """Register new connection"""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(sid)
        self.session_users[sid] = user_id
        logger.info(f"User {user_id} connected with session {sid}")

    async def disconnect(self, sid: str):
        """Remove connection"""
        user_id = self.session_users.get(sid)
        if user_id:
            self.active_connections[user_id].discard(sid)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            del self.session_users[sid]
            logger.info(f"User {user_id} disconnected session {sid}")

    async def send_to_user(self, user_id: str, event: str, data: dict):
        """Send event to specific user"""
        sessions = self.active_connections.get(user_id, set())
        for sid in sessions:
            await sio.emit(event, data, room=sid)

    async def broadcast(self, event: str, data: dict):
        """Broadcast event to all connected users"""
        await sio.emit(event, data)

    async def send_to_room(self, room: str, event: str, data: dict):
        """Send event to specific room"""
        await sio.emit(event, data, room=room)

    def get_user_sessions(self, user_id: str) -> Set[str]:
        """Get all session IDs for a user"""
        return self.active_connections.get(user_id, set())

    def is_user_connected(self, user_id: str) -> bool:
        """Check if user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global WebSocket manager instance
ws_manager = WebSocketManager()


# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Client connecting: {sid}")

    # Extract auth token from auth dict
    token = auth.get("token") if auth else None

    if not token:
        logger.warning(f"Connection rejected for {sid}: No token provided")
        return False

    # TODO: Validate token and extract user_id
    # For now, we'll accept the connection and validate in authenticate event
    logger.info(f"Client {sid} connected (pending authentication)")
    return True


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    await ws_manager.disconnect(sid)
    logger.info(f"Client {sid} disconnected")


@sio.event
async def authenticate(sid, data):
    """Handle authentication after connection"""
    try:
        from app.core.security import decode_token
        from app.core.database import AsyncSessionLocal
        from app.models.user import User
        from sqlalchemy import select

        token = data.get("token")
        if not token:
            await sio.emit("auth_error", {"error": "No token provided"}, room=sid)
            return

        # Decode token
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")

            if not user_id:
                await sio.emit("auth_error", {"error": "Invalid token"}, room=sid)
                return

            # Verify user exists
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()

                if not user or not user.is_active:
                    await sio.emit("auth_error", {"error": "User not found or inactive"}, room=sid)
                    return

            # Register connection
            await ws_manager.connect(sid, user_id)

            # Send success
            await sio.emit("authenticated", {
                "user_id": user_id,
                "message": "Successfully authenticated"
            }, room=sid)

            logger.info(f"Client {sid} authenticated as user {user_id}")

        except Exception as e:
            logger.error(f"Authentication error for {sid}: {str(e)}")
            await sio.emit("auth_error", {"error": "Authentication failed"}, room=sid)

    except Exception as e:
        logger.error(f"Error in authenticate handler: {str(e)}")
        await sio.emit("auth_error", {"error": "Internal error"}, room=sid)


@sio.event
async def join_room(sid, data):
    """Join a room for targeted messaging"""
    room = data.get("room")
    if room:
        sio.enter_room(sid, room)
        logger.info(f"Client {sid} joined room {room}")
        await sio.emit("room_joined", {"room": room}, room=sid)


@sio.event
async def leave_room(sid, data):
    """Leave a room"""
    room = data.get("room")
    if room:
        sio.leave_room(sid, room)
        logger.info(f"Client {sid} left room {room}")
        await sio.emit("room_left", {"room": room}, room=sid)


@sio.event
async def ping(sid):
    """Handle ping for connection health check"""
    await sio.emit("pong", {}, room=sid)
