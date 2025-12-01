"""Memory management service (local implementation)."""

from typing import Any


class MemoryService:
    """
    In-memory knowledge storage service.

    For v1.0, this is a simple in-memory implementation.
    Future versions will integrate Vertex AI Memory Bank.
    """

    def __init__(self):
        """Initialize memory service."""
        self._memories: dict[str, dict[str, Any]] = {}

    def store_memory(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> None:
        """Store memory for session."""
        if session_id not in self._memories:
            self._memories[session_id] = {}

        self._memories[session_id][key] = value

    def retrieve_memory(
        self,
        session_id: str,
        key: str,
    ) -> Any | None:
        """Retrieve memory for session."""
        if session_id not in self._memories:
            return None

        return self._memories[session_id].get(key)

    def list_memories(self, session_id: str) -> dict[str, Any]:
        """List all memories for session."""
        return self._memories.get(session_id, {})

    def consolidate_session_memory(
        self,
        session_id: str,
        project_memory_key: str,
    ) -> None:
        """
        Consolidate session learnings into project memory.

        This is simplified for v1.0. Future versions will use
        LLM-based extraction and semantic deduplication.
        """
        session_memories = self.list_memories(session_id)

        # Store session summary in project-level memory
        if "project" not in self._memories:
            self._memories["project"] = {}

        if project_memory_key not in self._memories["project"]:
            self._memories["project"][project_memory_key] = []

        self._memories["project"][project_memory_key].append({
            "session_id": session_id,
            "learnings": session_memories,
        })
