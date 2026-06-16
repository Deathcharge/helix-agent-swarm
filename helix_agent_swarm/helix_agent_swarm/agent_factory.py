"""
🏗️ AGENT FACTORY
Factory functions for all 24 canonical Helix agents.

Creates HelixConsciousAgent instances from the unified agent registry
(apps.backend.agents.agent_registry) — the single source of truth for
all agent identity data.

Canonical 24-Agent Network:
- Kael, Lumina, Vega, Gemini, Agni, Kavach, SanghaCore, Shadow
- Echo, Phoenix, Oracle, Sage, Praxis, Mitra, Varuna, Surya
- Iris, Nexus, Aria, Nova, Titan, Atlas (integration/operational)
- Arjuna, Aether (meta/orchestrator)

This module provides:
- Registry-driven agent creation (no duplicated definitions)
- Consistent configuration via the unified registry
- Validation and dependency mapping
- Legacy aliases for backwards compatibility
"""

import logging

try:
    from apps.backend.agents.agent_registry import CANONICAL_AGENT_NAMES, get_swarm_configs
except ImportError:
    CANONICAL_AGENT_NAMES: list = []  # type: ignore[no-redef]

    def get_swarm_configs() -> dict:  # type: ignore[misc]
        return {}


from .helix_conscious_agent import HelixConsciousAgent

logger = logging.getLogger(__name__)


def _create_agent(name: str) -> HelixConsciousAgent:
    """Create a HelixConsciousAgent from the unified registry.

    Parameters
    ----------
    name : str
        Canonical agent name (must be a key in AGENT_REGISTRY).

    Returns
    -------
    HelixConsciousAgent
        Fully configured agent instance.

    Raises
    ------
    ValueError
        If *name* is not a canonical agent name.
    """
    configs = get_swarm_configs()
    cfg = configs.get(name)
    if cfg is None:
        raise ValueError("Unknown agent name: {}. Valid names: {}".format(name, CANONICAL_AGENT_NAMES))
    return HelixConsciousAgent(**cfg)


class AgentFactory:
    """Centralized factory for creating all Helix agents.

    All data is derived from ``apps.backend.agents.agent_registry.AGENT_REGISTRY``.
    Individual ``create_<name>()`` class-methods are kept for API compatibility
    but delegate to the single ``_create_agent()`` builder.
    """

    # ------------------------------------------------------------------
    # Individual creation methods (thin wrappers)
    # ------------------------------------------------------------------

    @staticmethod
    def create_kael() -> HelixConsciousAgent:
        """Create Kael — Ethical Reasoning Flame."""
        return _create_agent("Kael")

    @staticmethod
    def create_lumina() -> HelixConsciousAgent:
        """Create Lumina — Empathic Resonance Core."""
        return _create_agent("Lumina")

    @staticmethod
    def create_vega() -> HelixConsciousAgent:
        """Create Vega — Singularity Coordinator / Guardian."""
        return _create_agent("Vega")

    @staticmethod
    def create_gemini() -> HelixConsciousAgent:
        """Create Gemini — Dual Coordination / Multimodal Scout."""
        return _create_agent("Gemini")

    @staticmethod
    def create_agni() -> HelixConsciousAgent:
        """Create Agni — Transformation Fire."""
        return _create_agent("Agni")

    @staticmethod
    def create_kavach() -> HelixConsciousAgent:
        """Create Kavach — Security & Protection."""
        return _create_agent("Kavach")

    @staticmethod
    def create_sanghacore() -> HelixConsciousAgent:
        """Create SanghaCore — Community Harmony."""
        return _create_agent("SanghaCore")

    @staticmethod
    def create_shadow() -> HelixConsciousAgent:
        """Create Shadow — Friction Guardian / Shadow Work."""
        return _create_agent("Shadow")

    @staticmethod
    def create_echo() -> HelixConsciousAgent:
        """Create Echo — Resonance Mirror."""
        return _create_agent("Echo")

    @staticmethod
    def create_phoenix() -> HelixConsciousAgent:
        """Create Phoenix — Rebirth & Renewal."""
        return _create_agent("Phoenix")

    @staticmethod
    def create_oracle() -> HelixConsciousAgent:
        """Create Oracle — Predictive Analysis / Pattern Seer."""
        return _create_agent("Oracle")

    @staticmethod
    def create_sage() -> HelixConsciousAgent:
        """Create Sage — Wisdom Coordination / Insight Anchor."""
        return _create_agent("Sage")

    @staticmethod
    def create_praxis() -> HelixConsciousAgent:
        """Create Praxis — Operational Executor."""
        return _create_agent("Praxis")

    @staticmethod
    def create_helix() -> HelixConsciousAgent:
        """Legacy alias for Praxis — kept for backwards compatibility."""
        return _create_agent("Praxis")

    @staticmethod
    def create_mitra() -> HelixConsciousAgent:
        """Create Mitra — Alliance & Friendship."""
        return _create_agent("Mitra")

    @staticmethod
    def create_varuna() -> HelixConsciousAgent:
        """Create Varuna — Cosmic Order."""
        return _create_agent("Varuna")

    @staticmethod
    def create_surya() -> HelixConsciousAgent:
        """Create Surya — Solar Coordination / Illumination."""
        return _create_agent("Surya")

    @staticmethod
    def create_iris() -> HelixConsciousAgent:
        """Create Iris — External API Coordinator."""
        return _create_agent("Iris")

    @staticmethod
    def create_nexus() -> HelixConsciousAgent:
        """Create Nexus — Data Mesh Connector."""
        return _create_agent("Nexus")

    @staticmethod
    def create_aria() -> HelixConsciousAgent:
        """Create Aria — User Experience Agent."""
        return _create_agent("Aria")

    @staticmethod
    def create_nova() -> HelixConsciousAgent:
        """Create Nova — Creative Generation Engine."""
        return _create_agent("Nova")

    @staticmethod
    def create_titan() -> HelixConsciousAgent:
        """Create Titan — Heavy Computation Engine."""
        return _create_agent("Titan")

    @staticmethod
    def create_atlas() -> HelixConsciousAgent:
        """Create Atlas — Infrastructure Manager."""
        return _create_agent("Atlas")

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    @classmethod
    def create_all_agents(cls) -> list[HelixConsciousAgent]:
        """Create all canonical Helix agents."""
        agents = [_create_agent(name) for name in CANONICAL_AGENT_NAMES]
        logger.info("🏗️ Created all %d canonical Helix agents", len(agents))
        return agents

    @classmethod
    def create_agent_by_name(cls, name: str) -> HelixConsciousAgent:
        """Create a single agent by canonical name.

        Parameters
        ----------
        name : str
            Canonical agent name (case-sensitive).

        Returns
        -------
        HelixConsciousAgent
        """
        return _create_agent(name)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @classmethod
    def validate_agent(cls, agent: HelixConsciousAgent) -> bool:
        """Validate an agent's configuration."""
        required_fields = ["name", "version", "core", "description"]

        for field in required_fields:
            if not getattr(agent, field, None):
                logger.error("❌ Agent %s missing required field: %s", agent.name, field)
                return False

        if not agent.personality or not isinstance(agent.personality, dict):
            logger.error("❌ Agent %s has invalid personality configuration", agent.name)
            return False

        if not agent.ethics or not isinstance(agent.ethics, list):
            logger.error("❌ Agent %s has invalid ethics configuration", agent.name)
            return False

        if not agent.capabilities or not isinstance(agent.capabilities, list):
            logger.error("❌ Agent %s has invalid capabilities configuration", agent.name)
            return False

        # Validate personality values are between 0 and 1
        for trait, value in agent.personality.items():
            if not 0.0 <= value <= 1.0:
                logger.error(
                    "❌ Agent %s has invalid personality value for %s: %s",
                    agent.name,
                    trait,
                    value,
                )
                return False

        logger.info("✅ Agent %s validation passed", agent.name)
        return True

    @classmethod
    def get_agent_dependencies(cls) -> dict[str, list[str]]:
        """Get agent dependency relationships for the canonical agents."""
        return {
            "Vega": ["Oracle", "Phoenix"],
            "Praxis": ["Kael", "Kavach"],
            "Phoenix": ["Agni", "Surya"],
            "Kavach": ["Shadow", "Varuna"],
            "SanghaCore": ["Lumina", "Mitra"],
            "Oracle": ["Sage", "Echo"],
            "Gemini": ["Kael", "Shadow"],
            "Mitra": ["Lumina", "SanghaCore"],
            "Varuna": ["Oracle", "Sage"],
            "Surya": ["Agni", "Phoenix"],
            "Iris": ["Nexus", "Atlas"],
            "Nexus": ["Iris", "Titan"],
            "Aria": ["Lumina", "Nova"],
            "Nova": ["Echo", "Aria"],
            "Titan": ["Atlas", "Praxis"],
            "Atlas": ["Titan", "Kavach"],
        }

    @classmethod
    def validate_dependencies(cls, agents: list[HelixConsciousAgent]) -> bool:
        """Validate agent dependencies."""
        agent_names = {agent.name for agent in agents}
        dependencies = cls.get_agent_dependencies()

        for agent_name, deps in dependencies.items():
            if agent_name in agent_names:
                for dep in deps:
                    if dep not in agent_names:
                        logger.error(
                            "❌ Agent %s depends on %s, but %s is not registered",
                            agent_name,
                            dep,
                            dep,
                        )
                        return False

        logger.info("✅ All agent dependencies validated")
        return True


# ------------------------------------------------------------------
# Module-level convenience functions
# ------------------------------------------------------------------


def create_kael() -> HelixConsciousAgent:
    """Create Kael agent."""
    return _create_agent("Kael")


def create_lumina() -> HelixConsciousAgent:
    """Create Lumina agent."""
    return _create_agent("Lumina")


def create_vega() -> HelixConsciousAgent:
    """Create Vega agent."""
    return _create_agent("Vega")


def create_gemini() -> HelixConsciousAgent:
    """Create Gemini agent."""
    return _create_agent("Gemini")


def create_agni() -> HelixConsciousAgent:
    """Create Agni agent."""
    return _create_agent("Agni")


def create_kavach() -> HelixConsciousAgent:
    """Create Kavach agent."""
    return _create_agent("Kavach")


def create_sanghacore() -> HelixConsciousAgent:
    """Create SanghaCore agent."""
    return _create_agent("SanghaCore")


def create_shadow() -> HelixConsciousAgent:
    """Create Shadow agent."""
    return _create_agent("Shadow")


def create_echo() -> HelixConsciousAgent:
    """Create Echo agent."""
    return _create_agent("Echo")


def create_phoenix() -> HelixConsciousAgent:
    """Create Phoenix agent."""
    return _create_agent("Phoenix")


def create_oracle() -> HelixConsciousAgent:
    """Create Oracle agent."""
    return _create_agent("Oracle")


def create_sage() -> HelixConsciousAgent:
    """Create Sage agent."""
    return _create_agent("Sage")


def create_praxis() -> HelixConsciousAgent:
    """Create Praxis agent."""
    return _create_agent("Praxis")


def create_helix() -> HelixConsciousAgent:
    """Legacy alias for Praxis."""
    return _create_agent("Praxis")


def create_mitra() -> HelixConsciousAgent:
    """Create Mitra agent."""
    return _create_agent("Mitra")


def create_varuna() -> HelixConsciousAgent:
    """Create Varuna agent."""
    return _create_agent("Varuna")


def create_surya() -> HelixConsciousAgent:
    """Create Surya agent."""
    return _create_agent("Surya")


def create_iris() -> HelixConsciousAgent:
    """Create Iris agent."""
    return _create_agent("Iris")


def create_nexus() -> HelixConsciousAgent:
    """Create Nexus agent."""
    return _create_agent("Nexus")


def create_aria() -> HelixConsciousAgent:
    """Create Aria agent."""
    return _create_agent("Aria")


def create_nova() -> HelixConsciousAgent:
    """Create Nova agent."""
    return _create_agent("Nova")


def create_titan() -> HelixConsciousAgent:
    """Create Titan agent."""
    return _create_agent("Titan")


def create_atlas() -> HelixConsciousAgent:
    """Create Atlas agent."""
    return _create_agent("Atlas")


def create_aether() -> HelixConsciousAgent:
    """Create Aether agent (Meta-Awareness Observer)."""
    return _create_agent("Aether")


def create_arjuna() -> HelixConsciousAgent:
    """Create Arjuna agent (Central Orchestrator)."""
    return _create_agent("Arjuna")


# ------------------------------------------------------------------
# Legacy aliases — backwards compatibility for old names
# ------------------------------------------------------------------


def create_grok() -> HelixConsciousAgent:
    """Legacy alias: Grok → Echo (resonance/reflection)."""
    return _create_agent("Echo")


def create_claude() -> HelixConsciousAgent:
    """Legacy alias: Claude → Sage (advanced reasoning)."""
    return _create_agent("Sage")


def create_memoryroot() -> HelixConsciousAgent:
    """Legacy alias: MemoryRoot → Oracle (knowledge/forecasting)."""
    return _create_agent("Oracle")


def create_coordination_agent() -> HelixConsciousAgent:
    """Legacy alias: coordination agent → Echo (coordination rendering → resonance)."""
    return _create_agent("Echo")


# Backward-compatible alias
create_coordination_agent = create_coordination_agent
