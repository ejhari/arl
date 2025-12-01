"""Event service for real-time event management"""

import json
import logging
from typing import Optional, List
from datetime import datetime

from app.core.redis import pubsub
from app.core.websocket import ws_manager, sio
from app.schemas.event import EventBase, BroadcastEvent, EventType

logger = logging.getLogger(__name__)


class EventService:
    """Service for managing real-time events"""

    def __init__(self):
        self.redis_channel = "arl:events"

    async def emit_event(
        self,
        event_type: EventType,
        data: dict,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """Emit event to specific user or broadcast"""
        event = EventBase(
            type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
        )

        # Publish to Redis for multi-server support
        await pubsub.publish(
            self.redis_channel,
            json.dumps(event.model_dump(mode="json"))
        )

        # Send directly if user is connected
        if user_id:
            await ws_manager.send_to_user(
                user_id,
                event_type.value,
                event.model_dump(mode="json")
            )
        else:
            # Broadcast to all
            await ws_manager.broadcast(
                event_type.value,
                event.model_dump(mode="json")
            )

    async def emit_to_users(
        self,
        event_type: EventType,
        data: dict,
        user_ids: List[str],
    ):
        """Emit event to multiple specific users"""
        event = EventBase(
            type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
        )

        for user_id in user_ids:
            await ws_manager.send_to_user(
                user_id,
                event_type.value,
                event.model_dump(mode="json")
            )

    async def emit_to_room(
        self,
        room: str,
        event_type: EventType,
        data: dict,
    ):
        """Emit event to a specific room"""
        event = EventBase(
            type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
        )

        await ws_manager.send_to_room(
            room,
            event_type.value,
            event.model_dump(mode="json")
        )

    async def broadcast(
        self,
        event_type: EventType,
        data: dict,
    ):
        """Broadcast event to all connected users"""
        event = EventBase(
            type=event_type,
            data=data,
            timestamp=datetime.utcnow(),
        )

        await ws_manager.broadcast(
            event_type.value,
            event.model_dump(mode="json")
        )

    async def emit_research_progress(
        self,
        research_id: str,
        user_id: str,
        progress: float,
        message: str,
        project_id: Optional[str] = None,
    ):
        """Emit research progress update"""
        await self.emit_event(
            EventType.RESEARCH_PROGRESS,
            {
                "research_id": research_id,
                "project_id": project_id,
                "progress": progress,
                "message": message,
                "status": "in_progress",
            },
            user_id=user_id,
        )

    async def emit_research_completed(
        self,
        research_id: str,
        user_id: str,
        results: dict,
        project_id: Optional[str] = None,
    ):
        """Emit research completion"""
        await self.emit_event(
            EventType.RESEARCH_COMPLETED,
            {
                "research_id": research_id,
                "project_id": project_id,
                "results": results,
                "status": "completed",
                "message": "Research completed successfully",
            },
            user_id=user_id,
        )

    async def emit_research_error(
        self,
        research_id: str,
        user_id: str,
        error: str,
        project_id: Optional[str] = None,
    ):
        """Emit research error"""
        await self.emit_event(
            EventType.RESEARCH_ERROR,
            {
                "research_id": research_id,
                "project_id": project_id,
                "error": error,
                "status": "error",
                "message": f"Research failed: {error}",
            },
            user_id=user_id,
        )

    async def emit_agent_output(
        self,
        agent_id: str,
        user_id: str,
        output: str,
        agent_type: Optional[str] = None,
    ):
        """Emit agent output"""
        await self.emit_event(
            EventType.AGENT_OUTPUT,
            {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "output": output,
            },
            user_id=user_id,
        )

    async def emit_cell_event(
        self,
        cell_id: str,
        project_id: str,
        user_id: str,
        action: str,
        cell_data: Optional[dict] = None,
    ):
        """Emit cell event"""
        event_type_map = {
            "created": EventType.CELL_CREATED,
            "updated": EventType.CELL_UPDATED,
            "deleted": EventType.CELL_DELETED,
            "executed": EventType.CELL_EXECUTED,
        }

        event_type = event_type_map.get(action, EventType.CELL_UPDATED)

        await self.emit_event(
            event_type,
            {
                "cell_id": cell_id,
                "project_id": project_id,
                "action": action,
                "cell_data": cell_data,
            },
            user_id=user_id,
        )

    async def listen_to_redis(self):
        """Listen to Redis pub/sub for events from other servers"""
        await pubsub.subscribe(self.redis_channel)

        async for message in pubsub.listen():
            try:
                event_data = json.loads(message["data"])
                event = EventBase(**event_data)

                # Re-broadcast to local connections
                if event.user_id:
                    await ws_manager.send_to_user(
                        event.user_id,
                        event.type.value,
                        event.model_dump(mode="json")
                    )
                else:
                    await ws_manager.broadcast(
                        event.type.value,
                        event.model_dump(mode="json")
                    )

            except Exception as e:
                logger.error(f"Error processing Redis event: {str(e)}")


# Global event service instance
event_service = EventService()
