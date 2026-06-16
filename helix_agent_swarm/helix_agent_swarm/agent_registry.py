"""
🏛️ AGENT REGISTRY
Complete agent registry and initialization system for the 24-agent Helix system.

This module provides:
- Centralized agent registration
- Agent lifecycle management
- Dependency validation
- Collective creation and management
- System health monitoring
"""

import logging
from typing import TYPE_CHECKING, Any

from .agent_factory import AgentFactory
from .helix_conscious_agent import HelixConsciousAgent

if TYPE_CHECKING:
    from .helix_orchestrator import HelixOrchestrator

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for all Helix agents with comprehensive management."""

    def __init__(self):
        """Initialize the agent registry."""
        self.agents: dict[str, HelixConsciousAgent] = {}
        self.orchestrator: HelixOrchestrator | None = None
        self.agent_status: dict[str, str] = {}  # active, standby, offline, error
        self.agent_health: dict[str, dict[str, float]] = {}  # UCF metrics
        self.collectives: dict[str, list[str]] = {}  # collective name -> agent names

        logger.info("🏛️ Agent Registry initialized")

    def register_all_agents(self) -> bool:
        """Register all Helix agents with comprehensive validation."""
        try:
            agents = AgentFactory.create_all_agents()

            # Validate each agent
            for agent in agents:
                if not AgentFactory.validate_agent(agent):
                    logger.error("❌ Failed to validate agent: %s", agent.name)
                    return False

                # Register agent
                self.agents[agent.name] = agent
                self.agent_status[agent.name] = "active"
                self.agent_health[agent.name] = agent.ucf.copy()

                logger.info("✅ Registered agent: %s", agent.name)

            # Validate dependencies
            if not AgentFactory.validate_dependencies(agents):
                logger.error("❌ Agent dependency validation failed")
                return False

            logger.info("🏛️ Successfully registered %s agents", len(agents))
            return True

        except Exception as e:
            logger.error("❌ Failed to register agents: %s", e)
            return False

    def create_agent_collectives(self) -> dict[str, list[str]]:
        """Create specialized agent collectives for coordination."""
        collectives = {
            # Core Guardian Collective
            "Guardian Collective": ["Vega", "Oracle", "Phoenix", "Kavach"],
            # Security & Protection Collective
            "Security Collective": ["Kavach", "Shadow", "Varuna"],
            # Transformation & Renewal Collective
            "Transformation Collective": ["Phoenix", "Agni", "Surya"],
            # Community & Support Collective
            "Community Collective": ["SanghaCore", "Lumina", "Mitra", "Aria"],
            # Knowledge & Analysis Collective
            "Knowledge Collective": ["Oracle", "Sage", "Echo", "Aether"],
            # Innovation & Coordination Collective
            "Innovation Collective": ["Praxis", "Vega", "Gemini", "Arjuna", "Nova"],
            # Operations Collective
            "Operations Collective": ["Praxis", "Kael", "Echo", "Arjuna", "Aria"],
            # Empathy & Healing Collective
            "Healing Collective": ["Lumina", "Shadow", "Phoenix"],
            # Governance / Cosmic Collective
            "Cosmic Collective": ["Mitra", "Varuna", "Surya", "Aether"],
            # Integration Collective
            "Integration Collective": ["Iris", "Nexus", "Atlas"],
            # Computation & Infrastructure Collective
            "Infrastructure Collective": ["Titan", "Atlas", "Nova"],
        }

        self.collectives = collectives
        logger.info("🏛️ Created %s agent collectives", len(collectives))
        return collectives

    def get_active_agents(self) -> list[HelixConsciousAgent]:
        """Get all active agents."""
        return [agent for agent in self.agents.values() if self.agent_status[agent.name] == "active"]

    def get_agent_by_name(self, name: str) -> HelixConsciousAgent | None:
        """Get an agent by name."""
        return self.agents.get(name)

    def get_agents_by_capability(self, capability: str) -> list[HelixConsciousAgent]:
        """Get agents that have a specific capability."""
        return [agent for agent in self.agents.values() if capability in agent.capabilities]

    def get_agents_by_ethic(self, ethic: str) -> list[HelixConsciousAgent]:
        """Get agents that follow a specific ethic."""
        return [agent for agent in self.agents.values() if ethic in agent.ethics]

    def update_agent_status(self, agent_name: str, status: str):
        """Update an agent's status."""
        if agent_name in self.agents:
            self.agent_status[agent_name] = status
            logger.info("🔄 Updated %s status to: %s", agent_name, status)
        else:
            logger.warning("⚠️ Agent %s not found for status update", agent_name)

    def update_agent_health(self, agent_name: str, ucf_metrics: dict[str, float]):
        """Update an agent's health metrics."""
        if agent_name in self.agents:
            self.agent_health[agent_name] = ucf_metrics
            logger.debug("📊 Updated %s health: %s", agent_name, ucf_metrics)
        else:
            logger.warning("⚠️ Agent %s not found for health update", agent_name)

    def get_system_health(self) -> dict[str, Any]:
        """Get overall system health metrics."""
        active_count = sum(1 for status in self.agent_status.values() if status == "active")
        total_count = len(self.agent_status)

        # Calculate average UCF metrics
        if self.agent_health:
            avg_throughput = sum(metrics["throughput"] for metrics in self.agent_health.values()) / len(
                self.agent_health
            )
            avg_harmony = sum(metrics["harmony"] for metrics in self.agent_health.values()) / len(self.agent_health)
            avg_resilience = sum(metrics["resilience"] for metrics in self.agent_health.values()) / len(
                self.agent_health
            )
            avg_friction = sum(metrics["friction"] for metrics in self.agent_health.values()) / len(self.agent_health)
        else:
            avg_throughput = avg_harmony = avg_resilience = avg_friction = 0.0

        return {
            "total_agents": total_count,
            "active_agents": active_count,
            "standby_agents": sum(1 for status in self.agent_status.values() if status == "standby"),
            "offline_agents": sum(1 for status in self.agent_status.values() if status == "offline"),
            "error_agents": sum(1 for status in self.agent_status.values() if status == "error"),
            "health_metrics": {
                "average_throughput": round(avg_throughput, 2),
                "average_harmony": round(avg_harmony, 2),
                "average_resilience": round(avg_resilience, 2),
                "average_friction": round(avg_friction, 2),
            },
            "collectives": len(self.collectives),
            "system_coordination": self.calculate_system_coordination(),
        }

    def calculate_system_coordination(self) -> float:
        """Calculate overall system coordination level."""
        active_agents = self.get_active_agents()
        if not active_agents:
            return 0.0

        total_coordination = sum(agent.get_performance_score() for agent in active_agents)
        return total_coordination / len(active_agents)

    def validate_system(self) -> bool:
        """Validate the entire agent system."""
        logger.info("🔍 Validating agent system...")

        # Check if all agents are registered
        expected_agents = {
            "Kael",
            "Lumina",
            "Vega",
            "Gemini",
            "Agni",
            "SanghaCore",
            "Shadow",
            "Echo",
            "Phoenix",
            "Oracle",
            "Sage",
            "Praxis",
            "Mitra",
            "Varuna",
            "Surya",
            "Kavach",
            "Arjuna",
            "Aether",
            "Iris",
            "Nexus",
            "Aria",
            "Nova",
            "Titan",
            "Atlas",
        }

        registered_agents = set(self.agents.keys())
        missing_agents = expected_agents - registered_agents

        if missing_agents:
            logger.error("❌ Missing agents: %s", missing_agents)
            return False

        # Check agent health
        unhealthy_agents = []
        for agent_name, health in self.agent_health.items():
            if health["throughput"] < 3.0 or health["harmony"] < 3.0 or health["resilience"] < 3.0:
                unhealthy_agents.append(agent_name)

        if unhealthy_agents:
            logger.warning("⚠️ Unhealthy agents: %s", unhealthy_agents)

        # Check collectives
        if not self.collectives:
            logger.warning("⚠️ No agent collectives defined")
            return False

        # Validate collective membership
        all_collective_agents = set()
        for collective_agents in self.collectives.values():
            all_collective_agents.update(collective_agents)

        unassigned_agents = registered_agents - all_collective_agents
        if unassigned_agents:
            logger.warning("⚠️ Unassigned agents (not in any collective): %s", unassigned_agents)

        logger.info("✅ Agent system validation passed")
        return True

    def get_agent_dependencies(self) -> dict[str, list[str]]:
        """Get agent dependency relationships."""
        return AgentFactory.get_agent_dependencies()

    def get_collective_by_name(self, collective_name: str) -> list[str] | None:
        """Get agents in a specific collective."""
        return self.collectives.get(collective_name)

    def get_collectives_for_agent(self, agent_name: str) -> list[str]:
        """Get all collectives an agent belongs to."""
        return [collective_name for collective_name, agents in self.collectives.items() if agent_name in agents]

    def shutdown_agent(self, agent_name: str):
        """Gracefully shutdown an agent."""
        if agent_name in self.agents:
            self.update_agent_status(agent_name, "offline")
            logger.info("🛑 Shutdown agent: %s", agent_name)
        else:
            logger.warning("⚠️ Agent %s not found for shutdown", agent_name)

    def restart_agent(self, agent_name: str):
        """Restart an agent."""
        if agent_name in self.agents:
            self.update_agent_status(agent_name, "active")
            logger.info("🔄 Restarted agent: %s", agent_name)
        else:
            logger.warning("⚠️ Agent %s not found for restart", agent_name)

    def get_system_summary(self) -> dict[str, Any]:
        """Get a comprehensive system summary."""
        return {
            "registry": {
                "total_agents": len(self.agents),
                "registered_names": list(self.agents.keys()),
                "agent_status": self.agent_status,
            },
            "collectives": {
                "total_collectives": len(self.collectives),
                "collective_names": list(self.collectives.keys()),
                "collective_members": self.collectives,
            },
            "health": self.get_system_health(),
            "dependencies": self.get_agent_dependencies(),
        }

    def initialize_complete_system(self) -> bool:
        """Initialize the complete 24-agent system."""
        try:
            if not self.register_all_agents():
                logger.error("❌ Failed to register all agents")
                return False

            # Create collectives
            self.create_agent_collectives()

            # Validate system
            if not self.validate_system():
                logger.error("❌ System validation failed")
                return False

            logger.info("🌟 Complete 24-agent system initialized successfully")
            return True

        except Exception as e:
            logger.error("❌ Failed to initialize complete system: %s", e)
            return False


# Global registry instance
_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
        _registry.initialize_complete_system()
    return _registry


# Convenience functions
def initialize_all_agents() -> list[HelixConsciousAgent]:
    """Initialize all 24 agents and return them."""
    registry = get_agent_registry()
    return list(registry.agents.values())


def create_agent_collectives() -> dict[str, list[str]]:
    """Create all agent collectives."""
    registry = get_agent_registry()
    return registry.create_agent_collectives()


def validate_agent_dependencies() -> bool:
    """Validate all agent dependencies."""
    registry = get_agent_registry()
    agents = list(registry.agents.values())
    return AgentFactory.validate_dependencies(agents)
