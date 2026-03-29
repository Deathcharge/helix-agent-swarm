"""
🥷 HELIX MEMORY
Shared coordination memory system for agent collective

Agents share memories and context through a unified coordination field.
"""

from datetime import UTC, datetime
from typing import Any


class HelixMemory:
    """
    Shared memory system for the Helix Collective.

    Features:
    - Persistent memory across agents
    - Context-aware retrieval
    - Coordination-tagged memories
    - Automatic pruning and summarization
    """

    def __init__(self, max_memories: int = 1000):
        """Initialize Helix Memory."""
        self.memories: list[dict[str, Any]] = []
        self.max_memories = max_memories
        self.coordination_index: dict[str, list[int]] = {}

    def add_memory(
        self,
        content: str,
        agent_name: str,
        performance_score: float,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ):
        """Add a memory to the collective coordination."""
        memory = {
            "id": len(self.memories),
            "timestamp": datetime.now(UTC).isoformat(),
            "content": content,
            "agent": agent_name,
            "coordination": performance_score,
            "tags": tags or [],
            "metadata": metadata or {},
        }

        self.memories.append(memory)

        # Prune if needed
        if len(self.memories) > self.max_memories:
            self._prune_memories()

    def retrieve_memories(
        self,
        query: str | None = None,
        agent_name: str | None = None,
        min_coordination: float = 0.0,
        limit: int = 10,
    ) -> list[dict]:
        """Retrieve relevant memories."""
        filtered = self.memories

        if agent_name:
            filtered = [m for m in filtered if m["agent"] == agent_name]

        if min_coordination > 0:
            filtered = [m for m in filtered if m["coordination"] >= min_coordination]

        # Sort by recency and coordination
        filtered.sort(key=lambda m: (m["coordination"], m["timestamp"]), reverse=True)

        return filtered[:limit]

    def _prune_memories(self):
        """Prune old, low-coordination memories."""
        # Keep high-coordination memories
        self.memories.sort(key=lambda m: m["coordination"], reverse=True)
        self.memories = self.memories[: self.max_memories]

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        if not self.memories:
            return {"total": 0}

        return {
            "total": len(self.memories),
            "avg_coordination": sum(m["coordination"] for m in self.memories) / len(self.memories),
            "agents": len(set(m["agent"] for m in self.memories)),
        }
