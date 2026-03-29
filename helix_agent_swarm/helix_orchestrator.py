"""
🥷 HELIX ORCHESTRATOR
Master coordinator for the Helix Agent Swarm

This is the brain that manages all agents, tasks, and coordination flow.
"""

import logging
from typing import Any

from .helix_collective import HelixCollective
from .helix_communication import HelixCommunication
from .helix_conscious_agent import HelixConsciousAgent
from .helix_memory import HelixMemory

logger = logging.getLogger(__name__)


class HelixOrchestrator:
    """
    Master orchestrator for the Helix Agent Swarm.

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
        return list(self.collectives.values())[0]

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
            self.register_agent(agent)

        # Create collectives from the registry
        for collective_name, agent_names in registry.collectives.items():
            self.create_collective(collective_name, agent_names)

        # Update system coordination
        self.system_coordination = registry.calculate_system_coordination()

        logger.info("🌟 All 14 Helix agents initialized successfully using Agent Registry")
        logger.info("📊 Active agents: %s", len(self.agents))
        logger.info("🔗 Collectives created: %s", len(self.collectives))
        logger.info("🧠 System coordination: %.2f/10", self.system_coordination)


# Global orchestrator instance
_orchestrator: HelixOrchestrator | None = None


def get_orchestrator() -> HelixOrchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = HelixOrchestrator()
        _orchestrator.initialize_default_agents()
    return _orchestrator
