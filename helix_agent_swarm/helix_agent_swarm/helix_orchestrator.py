"""
🥷 HELIX ORCHESTRATOR
Master coordinator for the agent swarm

This is the brain that manages all agents, tasks, and coordination flow.
"""

import json
import logging
from datetime import UTC, datetime
from time import monotonic
from typing import Any

from .helix_collective import HelixCollective
from .helix_communication import HelixCommunication
from .helix_conscious_agent import HelixConsciousAgent
from .helix_memory import HelixMemory

logger = logging.getLogger(__name__)

_SESSION_STATE_PREFIX = "helix:agent_swarm:session:"


class HelixOrchestrator:
    """
    Master orchestrator for the agent swarm.

    Responsibilities:
    - Agent lifecycle management
    - Task distribution
    - Coordination monitoring
    - Resource allocation
    - Collective coordination
    """

    def __init__(self):
        """Initialize the Helix Orchestrator."""
        self.agents: dict[str, HelixConsciousAgent] = {}
        self.collectives: dict[str, HelixCollective] = {}
        self.memory = HelixMemory()
        self.communication = HelixCommunication()

        # System state
        self.active_tasks: list[dict] = []
        self.system_coordination = 0.0

        logger.info("🌊 Helix Orchestrator initialized")

    def register_agent(self, agent: HelixConsciousAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.name] = agent
        logger.info("✅ Registered agent: %s", agent.name)

    def create_collective(
        self,
        name: str,
        agent_names: list[str],
    ) -> HelixCollective:
        """Create a new collective from registered agents."""
        agents = [self.agents[name] for name in agent_names if name in self.agents]

        collective = HelixCollective(agents=agents, name=name)
        self.collectives[name] = collective

        logger.info("🌊 Created collective: %s with %s agents", name, len(agents))
        return collective

    async def execute_task(
        self,
        task: str,
        collective_name: str | None = None,
        context: dict | None = None,
    ) -> dict[str, Any]:
        """
        Execute a task using the appropriate collective.

        Args:
            task: Task description
            collective_name: Which collective to use (or auto-select)
            context: Additional context

        Returns:
            Task result with conversation history
        """
        # Select or create collective
        if collective_name and collective_name in self.collectives:
            collective = self.collectives[collective_name]
        else:
            # Auto-select best collective based on task
            collective = self._select_collective_for_task(task)

        # Execute task
        conversation = await collective.initiate_conversation(task, context)

        # Update system coordination
        self.system_coordination = self.calculate_system_coordination()

        return {
            "task": task,
            "collective": collective.name,
            "conversation": conversation,
            "system_coordination": self.system_coordination,
            "result": "success",
        }

    def _select_collective_for_task(self, task: str) -> HelixCollective:
        """Select the best collective for a task."""
        # If no collectives exist, create a default one
        if not self.collectives:
            return self.create_collective("Default Collective", list(self.agents.keys()))

        # Return first available collective (would be more sophisticated in production)
        return next(iter(self.collectives.values()))

    def calculate_system_coordination(self) -> float:
        """Calculate overall system coordination."""
        if not self.agents:
            return 0.0

        total = sum(agent.get_performance_score() for agent in self.agents.values())
        return total / len(self.agents)

    def get_system_status(self) -> dict[str, Any]:
        """Get complete system status."""
        return {
            "agents": {name: agent.get_status() for name, agent in self.agents.items()},
            "collectives": {name: collective.get_status() for name, collective in self.collectives.items()},
            "memory": self.memory.get_stats(),
            "system_coordination": self.calculate_system_coordination(),
            "active_tasks": len(self.active_tasks),
        }

    def save_state(self) -> dict[str, Any]:
        """Serialize mutable orchestrator state for Redis-backed user sessions."""
        return {
            "saved_at": datetime.now(UTC).isoformat(),
            "agents": {name: agent.save_state() for name, agent in self.agents.items()},
            "collectives": {name: collective.save_state() for name, collective in self.collectives.items()},
            "memory": self.memory.save_state(),
            "active_tasks": self.active_tasks[-100:],
            "system_coordination": self.system_coordination,
        }

    def restore_state(self, state: dict[str, Any] | None) -> None:
        """Restore mutable orchestrator state on top of a fresh agent graph."""
        if not state:
            return

        for agent_name, agent_state in (state.get("agents") or {}).items():
            if agent_name in self.agents:
                self.agents[agent_name].restore_state(agent_state)
            else:
                self.agents[agent_name] = HelixConsciousAgent.load_state(agent_state)

        for collective_name, collective_state in (state.get("collectives") or {}).items():
            collective = self.collectives.get(collective_name)
            if collective is None:
                collective = self.create_collective(collective_name, collective_state.get("agent_names", []))
            collective.restore_state(collective_state, self.agents)

        self.memory.load_state(state.get("memory"))
        self.active_tasks = list(state.get("active_tasks", []))
        self.system_coordination = float(state.get("system_coordination", self.calculate_system_coordination()))

    def initialize_default_agents(self):
        """Initialize all 14 Helix agents using the new agent factory and registry."""
        from .agent_registry import get_agent_registry

        # Use the agent registry to initialize the complete system
        registry = get_agent_registry()

        if not registry.initialize_complete_system():
            logger.error("❌ Failed to initialize complete agent system")
            return

        # Register all agents from the registry
        for agent in registry.get_active_agents():
            self.register_agent(HelixConsciousAgent.load_state(agent.save_state()))

        # Create collectives from the registry
        for collective_name, agent_names in registry.collectives.items():
            self.create_collective(collective_name, agent_names)

        # Update system coordination
        self.system_coordination = registry.calculate_system_coordination()

        logger.info("🌟 All 24 Helix agents initialized successfully using Agent Registry")
        logger.info("📊 Active agents: %s", len(self.agents))
        logger.info("🔗 Collectives created: %s", len(self.collectives))
        logger.info("🧠 System coordination: %.2f/10", self.system_coordination)


def _build_orchestrator() -> HelixOrchestrator:
    """Create and initialize a fresh orchestrator instance."""
    orchestrator = HelixOrchestrator()
    orchestrator.initialize_default_agents()
    return orchestrator


# Cached template state — built once from a fully initialized orchestrator,
# then used to stamp out new instances via restore_state() without repeating
# the expensive agent-registry initialization.
_base_template_state: dict[str, Any] | None = None


def _get_or_build_orchestrator() -> HelixOrchestrator:
    """Return a fresh orchestrator, reusing a cached template state when possible.

    First call pays the full _build_orchestrator() cost and caches the resulting
    state dict.  Subsequent calls create a bare HelixOrchestrator() and restore
    the template — skipping get_agent_registry() / initialize_default_agents().
    """
    global _base_template_state

    if _base_template_state is not None:
        orchestrator = HelixOrchestrator()
        orchestrator.restore_state(_base_template_state)
        return orchestrator

    orchestrator = _build_orchestrator()
    _base_template_state = orchestrator.save_state()
    return orchestrator


async def _get_redis():
    """Get Redis for cross-worker swarm session state, if configured."""
    try:
        from apps.backend.core.redis_client import get_redis

        return await get_redis()
    except Exception as e:
        logger.debug("Redis unavailable for agent swarm sessions: %s", e)
        return None


def _session_state_key(session_key: str) -> str:
    return f"{_SESSION_STATE_PREFIX}{session_key}"


async def _load_session_state(session_key: str) -> dict[str, Any] | None:
    """Load serialized swarm session state from Redis, if available."""
    redis_client = await _get_redis()
    if redis_client is None:
        return None

    try:
        key = _session_state_key(session_key)
        raw = await redis_client.get(key)
        if not raw:
            return None
        await redis_client.expire(key, _SESSION_TTL_SECONDS)
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        payload = json.loads(raw)
        return payload.get("state", payload)
    except Exception as e:
        logger.warning("Failed to load swarm session %s from Redis: %s", session_key, e)
        return None


# Global orchestrator instance
_orchestrator: HelixOrchestrator | None = None
# Fallback session cache used only when Redis is unavailable.
_session_orchestrators: dict[str, tuple[float, HelixOrchestrator]] = {}
_SESSION_TTL_SECONDS = 3600
_MAX_SESSION_ORCHESTRATORS = 128


def _prune_session_orchestrators(now: float) -> None:
    """Drop expired or oldest session orchestrators to bound in-process state."""
    expired_sessions = [
        session_key
        for session_key, (last_accessed, _orchestrator_instance) in _session_orchestrators.items()
        if now - last_accessed > _SESSION_TTL_SECONDS
    ]
    for session_key in expired_sessions:
        _session_orchestrators.pop(session_key, None)

    overflow = len(_session_orchestrators) - _MAX_SESSION_ORCHESTRATORS
    if overflow <= 0:
        return

    oldest_sessions = sorted(
        _session_orchestrators.items(),
        key=lambda item: item[1][0],
    )[:overflow]
    for session_key, _value in oldest_sessions:
        _session_orchestrators.pop(session_key, None)


async def save_orchestrator(session_key: str | None, orchestrator: HelixOrchestrator) -> None:
    """Persist a caller-scoped orchestrator to Redis, or to local fallback cache."""
    if not session_key:
        return

    state = orchestrator.save_state()
    redis_client = await _get_redis()
    if redis_client is not None:
        try:
            payload = json.dumps({"state": state}, default=str)
            await redis_client.set(_session_state_key(session_key), payload, ex=_SESSION_TTL_SECONDS)
            _session_orchestrators.pop(session_key, None)
            return
        except Exception as e:
            logger.warning("Failed to persist swarm session %s to Redis: %s", session_key, e)

    logger.warning(
        "Redis unavailable — storing swarm session %s in-memory (will not survive restarts)",
        session_key,
    )
    now = monotonic()
    _prune_session_orchestrators(now)
    _session_orchestrators[session_key] = (now, orchestrator)


async def get_orchestrator(session_key: str | None = None) -> HelixOrchestrator:
    """Get the legacy global orchestrator or a caller-scoped Redis-backed session."""
    global _orchestrator
    if not session_key:
        if _orchestrator is None:
            _orchestrator = _get_or_build_orchestrator()
        return _orchestrator

    state = await _load_session_state(session_key)
    if state is not None:
        orchestrator = _get_or_build_orchestrator()
        orchestrator.restore_state(state)
        return orchestrator

    redis_client = await _get_redis()
    if redis_client is not None:
        orchestrator = _get_or_build_orchestrator()
        await save_orchestrator(session_key, orchestrator)
        return orchestrator

    # Redis unavailable — fall back to in-memory dict (non-durable)
    now = monotonic()
    _prune_session_orchestrators(now)

    cached = _session_orchestrators.get(session_key)
    if cached is not None:
        _session_orchestrators[session_key] = (now, cached[1])
        return cached[1]

    logger.warning(
        "Redis unavailable — creating ephemeral in-memory orchestrator for session %s "
        "(state will not persist across restarts or workers)",
        session_key,
    )
    orchestrator = _get_or_build_orchestrator()
    _session_orchestrators[session_key] = (now, orchestrator)
    return orchestrator
