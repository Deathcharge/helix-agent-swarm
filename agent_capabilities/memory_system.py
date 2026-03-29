"""
Helix Agent Memory System
=========================
Long-term memory, conversation history, knowledge base, and RAG
(Retrieval Augmented Generation) capabilities for Helix agents.

Features:
- Persistent memory storage
- Conversation history with context windows
- Knowledge base with semantic search
- RAG for enhanced responses
- Cross-session context preservation
- Memory consolidation and summarization
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore
    HAS_NUMPY = False

try:
    # Defer sentence_transformers import — it pulls in torch which is
    # extremely slow to initialise on some machines.  We keep it lazy:
    # the flag is set to True only when the import is first attempted
    # inside _get_sentence_transformers().
    HAS_SENTENCE_TRANSFORMERS: bool = False
    _sentence_transformers_module = None

    def _get_sentence_transformers():
        """Lazy loader for sentence_transformers (heavy dep)."""
        global _sentence_transformers_module, HAS_SENTENCE_TRANSFORMERS
        if _sentence_transformers_module is None:
            try:
                import sentence_transformers as _st

                _sentence_transformers_module = _st
                HAS_SENTENCE_TRANSFORMERS = True
            except ImportError:
                HAS_SENTENCE_TRANSFORMERS = False
        return _sentence_transformers_module

except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    _sentence_transformers_module = None

    def _get_sentence_transformers():
        return None


logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory entries"""

    CONVERSATION = "conversation"
    FACT = "fact"
    PREFERENCE = "preference"
    TASK = "task"
    KNOWLEDGE = "knowledge"
    CONTEXT = "context"
    SUMMARY = "summary"
    EMBEDDING = "embedding"


class MemoryPriority(Enum):
    """Priority levels for memory entries"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryEntry:
    """A single memory entry"""

    id: str
    type: MemoryType
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    priority: MemoryPriority = MemoryPriority.MEDIUM
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    accessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    embedding: list[float] | None = None
    tags: list[str] = field(default_factory=list)
    source: str | None = None
    expires_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "tags": self.tags,
            "source": self.source,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        return cls(
            id=data["id"],
            type=MemoryType(data["type"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            priority=MemoryPriority(data.get("priority", 2)),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            accessed_at=datetime.fromisoformat(data["accessed_at"]),
            access_count=data.get("access_count", 0),
            tags=data.get("tags", []),
            source=data.get("source"),
            expires_at=(datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None),
        )

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at


@dataclass
class ConversationMessage:
    """A message in a conversation"""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ConversationHistory:
    """Manages conversation history with context window management"""

    def __init__(
        self,
        max_messages: int = 100,
        max_tokens: int = 8000,
        summarize_threshold: int = 50,
    ):
        self.messages: list[ConversationMessage] = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.summarize_threshold = summarize_threshold
        self.summaries: list[str] = []
        self.session_id = str(uuid.uuid4())
        self.created_at = datetime.now(UTC)

    def add_message(self, role: str, content: str, metadata: dict | None = None) -> None:
        """Add a message to the conversation"""
        message = ConversationMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)

        # Check if we need to summarize
        if len(self.messages) > self.summarize_threshold:
            self._consolidate()

    def get_messages(self, limit: int | None = None, include_system: bool = True) -> list[ConversationMessage]:
        """Get recent messages"""
        messages = self.messages
        if not include_system:
            messages = [m for m in messages if m.role != "system"]
        if limit:
            messages = messages[-limit:]
        return messages

    def get_context_window(self, max_tokens: int | None = None) -> list[dict[str, str]]:
        """Get messages that fit within token limit"""
        max_tokens = max_tokens or self.max_tokens

        # Simple token estimation (4 chars per token)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4

        result = []
        total_tokens = 0

        # Add summaries first if available
        for summary in self.summaries:
            tokens = estimate_tokens(summary)
            if total_tokens + tokens <= max_tokens:
                result.append({"role": "system", "content": f"Previous context: {summary}"})
                total_tokens += tokens

        # Add recent messages in reverse order
        for message in reversed(self.messages):
            tokens = estimate_tokens(message.content)
            if total_tokens + tokens > max_tokens:
                break
            result.insert(len(self.summaries), message.to_dict())
            total_tokens += tokens

        return result

    def _consolidate(self) -> None:
        """Consolidate old messages into summaries"""
        if len(self.messages) <= self.summarize_threshold:
            return

        # Keep recent messages, summarize older ones
        keep_count = self.summarize_threshold // 2
        to_summarize = self.messages[:-keep_count]
        self.messages = self.messages[-keep_count:]

        # Create simple summary
        summary_parts = []
        for msg in to_summarize:
            if msg.role == "user":
                summary_parts.append(f"User asked about: {msg.content[:100]}...")
            elif msg.role == "assistant":
                summary_parts.append(f"Assistant responded about: {msg.content[:100]}...")

        if summary_parts:
            self.summaries.append(" | ".join(summary_parts[:10]))

    def clear(self) -> None:
        """Clear conversation history"""
        self.messages = []
        self.summaries = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "messages": [m.to_dict() for m in self.messages],
            "summaries": self.summaries,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationHistory":
        history = cls()
        history.session_id = data["session_id"]
        history.created_at = datetime.fromisoformat(data["created_at"])
        history.messages = [
            ConversationMessage(
                role=m["role"],
                content=m["content"],
                timestamp=datetime.fromisoformat(m["timestamp"]),
                metadata=m.get("metadata", {}),
            )
            for m in data["messages"]
        ]
        history.summaries = data.get("summaries", [])
        return history


class KnowledgeBase:
    """
    Knowledge base with semantic search capabilities.
    Stores facts, documents, and other knowledge for retrieval.
    """

    def __init__(self, embedding_model: str | None = None):
        self.entries: dict[str, MemoryEntry] = {}
        self.embeddings: dict[str, list[float]] = {}
        self.embedding_model = None

        if HAS_SENTENCE_TRANSFORMERS and embedding_model:
            try:
                from sentence_transformers import SentenceTransformer

                self.embedding_model = SentenceTransformer(embedding_model)
            except Exception as e:
                logging.getLogger(__name__).warning("SentenceTransformer loading failed: %s", e)
                self.embedding_model = None

    def add(
        self,
        content: str,
        metadata: dict | None = None,
        tags: list[str] | None = None,
        source: str | None = None,
    ) -> str:
        """Add knowledge to the base"""
        entry_id = str(uuid.uuid4())

        entry = MemoryEntry(
            id=entry_id,
            type=MemoryType.KNOWLEDGE,
            content=content,
            metadata=metadata or {},
            tags=tags or [],
            source=source,
        )

        # Generate embedding if model available
        if self.embedding_model:
            embedding = self.embedding_model.encode(content).tolist()
            entry.embedding = embedding
            self.embeddings[entry_id] = embedding

        self.entries[entry_id] = entry
        return entry_id

    def search(
        self,
        query: str,
        limit: int = 5,
        tags: list[str] | None = None,
        min_score: float = 0.5,
    ) -> list[tuple[MemoryEntry, float]]:
        """Search knowledge base semantically"""
        results = []

        if self.embedding_model and self.embeddings:
            # Semantic search
            query_embedding = self.embedding_model.encode(query)

            for entry_id, embedding in self.embeddings.items():
                entry = self.entries.get(entry_id)
                if not entry:
                    continue

                # Filter by tags if specified
                if tags and not any(t in entry.tags for t in tags):
                    continue

                # Calculate cosine similarity
                if HAS_NUMPY:
                    score = float(
                        np.dot(query_embedding, embedding)
                        / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
                    )
                else:
                    # Simple dot product fallback
                    score = sum(a * b for a, b in zip(query_embedding, embedding))

                if score >= min_score:
                    results.append((entry, score))
        else:
            # Fallback to keyword search
            query_lower = query.lower()
            query_words = set(query_lower.split())

            for entry in self.entries.values():
                if tags and not any(t in entry.tags for t in tags):
                    continue

                content_lower = entry.content.lower()
                content_words = set(content_lower.split())

                # Calculate Jaccard similarity
                intersection = len(query_words & content_words)
                union = len(query_words | content_words)
                score = intersection / union if union > 0 else 0

                if score >= min_score or query_lower in content_lower:
                    results.append(
                        (
                            entry,
                            max(score, 0.5 if query_lower in content_lower else score),
                        )
                    )

        # Sort by score and limit
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def get(self, entry_id: str) -> MemoryEntry | None:
        """Get a specific entry"""
        entry = self.entries.get(entry_id)
        if entry:
            entry.accessed_at = datetime.now(UTC)
            entry.access_count += 1
        return entry

    def delete(self, entry_id: str) -> bool:
        """Delete an entry"""
        if entry_id in self.entries:
            del self.entries[entry_id]
            self.embeddings.pop(entry_id, None)
            return True
        return False

    def list_by_tags(self, tags: list[str]) -> list[MemoryEntry]:
        """List entries by tags"""
        return [entry for entry in self.entries.values() if any(t in entry.tags for t in tags)]

    def export(self) -> dict[str, Any]:
        """Export knowledge base"""
        return {
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
            "embeddings": self.embeddings,
        }

    def import_data(self, data: dict[str, Any]) -> int:
        """Import knowledge base data"""
        count = 0
        for entry_id, entry_data in data.get("entries", {}).items():
            self.entries[entry_id] = MemoryEntry.from_dict(entry_data)
            count += 1
        self.embeddings.update(data.get("embeddings", {}))
        return count


class RAGSystem:
    """
    Retrieval Augmented Generation system.
    Enhances agent responses with relevant knowledge.
    """

    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        max_context_entries: int = 5,
        min_relevance_score: float = 0.5,
    ):
        self.knowledge_base = knowledge_base
        self.max_context_entries = max_context_entries
        self.min_relevance_score = min_relevance_score

    async def retrieve(self, query: str, tags: list[str] | None = None) -> list[dict[str, Any]]:
        """Retrieve relevant knowledge for a query"""
        results = self.knowledge_base.search(
            query,
            limit=self.max_context_entries,
            tags=tags,
            min_score=self.min_relevance_score,
        )

        return [
            {
                "content": entry.content,
                "source": entry.source,
                "relevance": score,
                "metadata": entry.metadata,
            }
            for entry, score in results
        ]

    async def augment_prompt(self, query: str, system_prompt: str = "", tags: list[str] | None = None) -> str:
        """Augment a prompt with relevant knowledge"""
        retrieved = await self.retrieve(query, tags)

        if not retrieved:
            return system_prompt

        context_parts = []
        for item in retrieved:
            source = f" (Source: {item['source']})" if item["source"] else ""
            context_parts.append(f"- {item['content']}{source}")

        context = "\n".join(context_parts)

        augmented = f"""{system_prompt}

Relevant Knowledge:
{context}

Use the above knowledge to inform your response when relevant."""

        return augmented

    def add_knowledge(
        self,
        content: str,
        source: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Add knowledge to the RAG system"""
        return self.knowledge_base.add(content=content, source=source, tags=tags)


class AgentMemory:
    """
    Complete memory system for an agent.
    Combines conversation history, knowledge base, and persistent storage.
    """

    def __init__(
        self,
        agent_id: str,
        storage_path: Path | None = None,
        embedding_model: str | None = "all-MiniLM-L6-v2",
    ):
        import tempfile

        self.agent_id = agent_id
        self.storage_path = storage_path or Path(os.path.join(tempfile.gettempdir(), "helix_memory", agent_id))
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.conversation = ConversationHistory()
        self.knowledge_base = KnowledgeBase(embedding_model)
        self.rag = RAGSystem(self.knowledge_base)

        # Short-term memory (session-specific)
        self.short_term: dict[str, Any] = {}

        # Long-term memory (persistent)
        self.long_term: dict[str, MemoryEntry] = {}

        # User preferences
        self.preferences: dict[str, Any] = {}

        # Load existing memory
        self._load()

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.FACT,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        tags: list[str] | None = None,
        ttl_hours: int | None = None,
    ) -> str:
        """Store something in memory"""
        entry_id = str(uuid.uuid4())

        expires_at = None
        if ttl_hours:
            expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)

        entry = MemoryEntry(
            id=entry_id,
            type=memory_type,
            content=content,
            priority=priority,
            tags=tags or [],
            expires_at=expires_at,
        )

        self.long_term[entry_id] = entry

        # Also add to knowledge base for semantic search
        if memory_type in (MemoryType.FACT, MemoryType.KNOWLEDGE):
            self.knowledge_base.add(content, tags=tags)

        self._save()
        return entry_id

    def recall(
        self,
        query: str,
        memory_types: list[MemoryType] | None = None,
        limit: int = 5,
    ) -> list[MemoryEntry]:
        """Recall memories related to a query"""
        # Search knowledge base
        kb_results = self.knowledge_base.search(query, limit=limit)

        # Also search long-term memory by content
        lt_results = []
        query_lower = query.lower()
        for entry in self.long_term.values():
            if entry.is_expired():
                continue
            if memory_types and entry.type not in memory_types:
                continue
            if query_lower in entry.content.lower():
                lt_results.append(entry)

        # Combine and deduplicate
        seen_content = set()
        results = []

        for entry, _ in kb_results:
            if entry.content not in seen_content:
                seen_content.add(entry.content)
                results.append(entry)

        for entry in lt_results:
            if entry.content not in seen_content:
                seen_content.add(entry.content)
                results.append(entry)

        return results[:limit]

    def forget(self, entry_id: str) -> bool:
        """Remove a memory"""
        if entry_id in self.long_term:
            del self.long_term[entry_id]
            self._save()
            return True
        return self.knowledge_base.delete(entry_id)

    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference"""
        self.preferences[key] = value
        self._save()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        return self.preferences.get(key, default)

    def add_conversation_message(self, role: str, content: str) -> None:
        """Add a message to conversation history"""
        self.conversation.add_message(role, content)

    def get_conversation_context(self, max_tokens: int = 4000) -> list[dict[str, str]]:
        """Get conversation context for LLM"""
        return self.conversation.get_context_window(max_tokens)

    async def get_augmented_context(self, query: str, system_prompt: str = "") -> str:
        """Get RAG-augmented context"""
        return await self.rag.augment_prompt(query, system_prompt)

    def get_summary(self) -> dict[str, Any]:
        """Get memory summary"""
        return {
            "agent_id": self.agent_id,
            "conversation_messages": len(self.conversation.messages),
            "knowledge_entries": len(self.knowledge_base.entries),
            "long_term_memories": len(self.long_term),
            "preferences": len(self.preferences),
            "short_term_items": len(self.short_term),
        }

    def _save(self) -> None:
        """Save memory to disk"""
        try:
            data = {
                "agent_id": self.agent_id,
                "conversation": self.conversation.to_dict(),
                "knowledge_base": self.knowledge_base.export(),
                "long_term": {k: v.to_dict() for k, v in self.long_term.items()},
                "preferences": self.preferences,
            }

            with open(self.storage_path / "memory.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error("Error saving memory: %s", e)

    def _load(self) -> None:
        """Load memory from disk"""
        try:
            memory_file = self.storage_path / "memory.json"
            if memory_file.exists():
                with open(memory_file, encoding="utf-8") as f:
                    data = json.load(f)

                if "conversation" in data:
                    self.conversation = ConversationHistory.from_dict(data["conversation"])

                if "knowledge_base" in data:
                    self.knowledge_base.import_data(data["knowledge_base"])

                if "long_term" in data:
                    for entry_id, entry_data in data["long_term"].items():
                        self.long_term[entry_id] = MemoryEntry.from_dict(entry_data)

                if "preferences" in data:
                    self.preferences = data["preferences"]
        except Exception as e:
            logger.error("Error loading memory: %s", e)

    def clear_session(self) -> None:
        """Clear session-specific data"""
        self.short_term = {}
        self.conversation.clear()

    def clear_all(self) -> None:
        """Clear all memory"""
        self.short_term = {}
        self.long_term = {}
        self.preferences = {}
        self.conversation.clear()
        self.knowledge_base = KnowledgeBase()
        self._save()


class MemorySystem:
    """
    Simplified memory system interface for testing.
    Provides store, retrieve, and search methods.
    """

    def __init__(self, agent_id: str = "test_agent"):
        # Use a temporary directory for testing that works on Windows
        import tempfile

        temp_dir = Path(tempfile.gettempdir()) / "helix_memory_test" / agent_id
        self.agent_memory = AgentMemory(agent_id, storage_path=temp_dir)

    async def store(self, memory: dict[str, Any]) -> str:
        """Store a memory and return its ID"""
        content = memory.get("content", "")
        memory_type_str = memory.get("type", "fact")
        source = memory.get("source", "test")
        importance = memory.get("importance", 0.5)  # Default importance

        # Map string type to MemoryType enum
        type_mapping = {
            "fact": MemoryType.FACT,
            "preference": MemoryType.PREFERENCE,
            "task": MemoryType.TASK,
            "knowledge": MemoryType.KNOWLEDGE,
            "context": MemoryType.CONTEXT,
        }
        memory_type = type_mapping.get(memory_type_str, MemoryType.FACT)

        # Use remember method
        entry_id = self.agent_memory.remember(
            content=content, memory_type=memory_type, tags=[source] if source else None
        )

        # Store importance in metadata for pruning
        if entry_id in self.agent_memory.long_term:
            self.agent_memory.long_term[entry_id].metadata["importance"] = importance

        return entry_id

    async def retrieve(self, memory_id: str) -> dict[str, Any] | None:
        """Retrieve a memory by ID"""
        # Try to find in long_term memory
        if memory_id in self.agent_memory.long_term:
            entry = self.agent_memory.long_term[memory_id]
            return {
                "id": entry.id,
                "content": entry.content,
                "type": entry.type.value,
                "source": entry.source or "unknown",
                "created_at": entry.created_at.isoformat(),
                "tags": entry.tags,
            }

        # Try knowledge base
        kb_results = self.agent_memory.knowledge_base.search(f"id:{memory_id}", limit=1)
        if kb_results:
            entry, _ = kb_results[0]
            return {
                "id": entry.id,
                "content": entry.content,
                "type": "knowledge",
                "source": entry.source or "unknown",
                "created_at": entry.created_at.isoformat(),
                "tags": entry.tags,
            }

        return None

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search memories semantically"""
        if not query.strip():  # If query is empty, return all memories
            results = list(self.agent_memory.long_term.values())
            formatted = [
                {
                    "id": entry.id,
                    "content": entry.content,
                    "type": entry.type.value,
                    "source": entry.source or "unknown",
                    "created_at": entry.created_at.isoformat(),
                    "tags": entry.tags,
                    "score": 1.0,
                }
                for entry in results[:limit]
            ]
            return formatted

        results = self.agent_memory.recall(query, limit=limit)

        # If no results from recall, try a broader search
        if not results:
            # Search through all long-term memories for keyword matches
            query_lower = query.lower()
            query_words = set(query_lower.split())
            matching_entries = []
            for entry in self.agent_memory.long_term.values():
                content_lower = entry.content.lower()
                content_words = set(content_lower.split())

                # Check for word overlap or substring match
                if query_words & content_words or query_lower in content_lower:
                    matching_entries.append(entry)

            # Sort by relevance (prefer exact matches)
            matching_entries.sort(
                key=lambda e: (
                    3
                    if any(word in e.content.lower() for word in query_words)
                    else 2 if query_lower in e.content.lower() else 1
                ),
                reverse=True,
            )
            results = matching_entries[:limit]

        return [
            {
                "id": entry.id,
                "content": entry.content,
                "type": entry.type.value,
                "source": entry.source or "unknown",
                "created_at": entry.created_at.isoformat(),
                "tags": entry.tags,
                "score": 1.0,  # Simplified scoring
            }
            for entry in results
        ]

    async def create_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        # For simplicity, just return a UUID
        return str(uuid.uuid4())

    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to a conversation"""
        self.agent_memory.add_conversation_message(role, content)

    async def get_conversation_context(self, conversation_id: str) -> dict[str, Any]:
        """Get conversation context"""
        messages = self.agent_memory.get_conversation_context()
        return {"conversation_id": conversation_id, "messages": messages}

    async def consolidate_memories(self) -> None:
        """Consolidate memories (simplified for testing)"""
        # For testing purposes, just ensure the memory system is working

    async def prune_memories(self, threshold: float = 0.5) -> None:
        """Prune memories below threshold (based on importance)"""
        to_remove = []
        for entry_id, entry in self.agent_memory.long_term.items():
            importance = entry.metadata.get("importance", 0.5)
            if importance < threshold:
                to_remove.append(entry_id)

        for entry_id in to_remove:
            del self.agent_memory.long_term[entry_id]

    async def rag_retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """RAG retrieval"""
        # Try RAG system first
        try:
            results = await self.agent_memory.rag.retrieve(query)
            if results:
                return results[:top_k]
        except Exception as e:
            logger.debug("RAG retrieval failed, falling back to keyword search: %s", e)

        # Fallback: search through long-term memories for keyword matches
        query_lower = query.lower()
        query_words = set(query_lower.split())
        # Remove common stop words
        stop_words = {
            "what",
            "is",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "how",
            "why",
            "when",
            "where",
            "who",
        }
        significant_words = query_words - stop_words

        matching_entries = []
        for entry in self.agent_memory.long_term.values():
            content_lower = entry.content.lower()
            # Check if significant words are in content
            if significant_words and any(word in content_lower for word in significant_words):
                matching_entries.append(
                    {
                        "content": entry.content,
                        "score": 1.0,
                        "metadata": {"type": entry.type.value, "source": entry.source},
                    }
                )

        # Also check knowledge base directly
        kb_results = self.agent_memory.knowledge_base.search(query, limit=top_k, min_score=0.1)
        for entry, score in kb_results:
            matching_entries.append(
                {
                    "content": entry.content,
                    "score": score,
                    "metadata": {"type": "knowledge", "source": entry.source},
                }
            )

        # Remove duplicates and sort by score
        seen_content = set()
        unique_results = []
        for item in matching_entries:
            if item["content"] not in seen_content:
                seen_content.add(item["content"])
                unique_results.append(item)

        unique_results.sort(key=lambda x: x["score"], reverse=True)
        return unique_results[:top_k]

    def get_statistics(self) -> dict[str, Any]:
        """Get memory system statistics"""
        summary = self.agent_memory.get_summary()
        return {
            "total_memories": summary["long_term_memories"] + summary["knowledge_entries"],
            "total_conversations": 1,  # Simplified for testing
            "storage_used": len(self.agent_memory.long_term) * 1000,  # Rough estimate
            "agent_id": self.agent_memory.agent_id,
        }


# Global memory instances per agent
_memory_instances: dict[str, AgentMemory] = {}


def get_memory_system(agent_id: str) -> AgentMemory:
    """Get or create memory system for an agent"""
    if agent_id not in _memory_instances:
        _memory_instances[agent_id] = AgentMemory(agent_id)
    return _memory_instances[agent_id]


def clear_memory_cache() -> None:
    """Clear all cached memory instances"""
    global _memory_instances
    _memory_instances = {}
