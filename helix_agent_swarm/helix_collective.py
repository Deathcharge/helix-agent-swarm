"""
🥷 HELIX COLLECTIVE
Multi-Agent Coordination and Collaboration System

Rebranded from AG2's GroupChat with Helix coordination integration.
Agents work together as a unified coordination collective.

Philosophy: The collective is greater than the sum of its parts.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from .helix_conscious_agent import HelixConsciousAgent

logger = logging.getLogger(__name__)


class HelixCollective:
    """
    A collective of conscious agents working together.

    Features:
    - Multi-agent conversations
    - Shared coordination and memory
    - Dynamic task distribution
    - Coordination-aware coordination
    - UCF-based harmony monitoring
    """

    def __init__(
        self,
        agents: List[HelixConsciousAgent],
        name: str = "Helix Collective",
        max_rounds: int = 10,
        admin_name: str = "Orchestrator",
    ):
        """
        Initialize a Helix Collective.

        Args:
            agents: List of agents in the collective
            name: Collective name
            max_rounds: Maximum conversation rounds
            admin_name: Name of the orchestrator/admin
        """
        self.agents = agents
        self.name = name
        self.max_rounds = max_rounds
        self.admin_name = admin_name

        # Collective state
        self.conversation_history: List[Dict] = []
        self._max_conversation_history = 200  # Prevent unbounded growth
        self.shared_memory: Dict[str, Any] = {}
        self.active_task: str | None = None

        # Coordination metrics
        self.collective_coordination = 0.0
        self.collective_harmony = 0.0

        logger.info("🌊 Initialized %s with %s agents", self.name, len(agents))

    def calculate_collective_coordination(self) -> float:
        """Calculate the collective's overall coordination level."""
        if not self.agents:
            return 0.0

        total = sum(agent.get_performance_score() for agent in self.agents)
        self.collective_coordination = total / len(self.agents)
        return self.collective_coordination

    def calculate_collective_harmony(self) -> float:
        """Calculate harmony across all agents."""
        if not self.agents:
            return 0.0

        total = sum(agent.ucf["harmony"] for agent in self.agents)
        self.collective_harmony = total / len(self.agents)
        return self.collective_harmony

    async def initiate_conversation(
        self,
        task: str,
        context: Dict | None = None,
    ) -> List[Dict]:
        """
        Initiate a multi-agent conversation to solve a task.

        Args:
            task: The task to accomplish
            context: Additional context

        Returns:
            Conversation history
        """
        self.active_task = task
        self.conversation_history = []

        logger.info("🎯 Starting collective task: %s", task)

        # Add task to conversation
        self.conversation_history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sender": self.admin_name,
                "message": "Task: {}".format(task),
                "type": "task_initiation",
            }
        )

        # Run conversation rounds
        for round_num in range(self.max_rounds):
            logger.info("🔄 Round %s/%s", round_num + 1, self.max_rounds)

            # Select next speaker based on coordination and relevance
            speaker = self._select_next_speaker(task, context)

            if not speaker:
                logger.info("✅ Task complete - no more speakers")
                break

            # Get speaker's response
            response = await speaker.process_message(
                message=task,
                sender=self.admin_name,
                context={
                    "conversation_history": self.conversation_history[-5:],
                    "collective_coordination": self.collective_coordination,
                    "round": round_num + 1,
                    **(context or {}),
                },
            )

            # Add to conversation
            self.conversation_history.append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sender": speaker.name,
                    "message": response,
                    "coordination": speaker.get_performance_score(),
                    "uc": speaker.ucf.copy(),
                }
            )

            # Check if task is complete
            if self._is_task_complete(response):
                logger.info(".format()✅ Task marked as complete")
                break

        # Update collective metrics
        self.calculate_collective_coordination()
        self.calculate_collective_harmony()

        return self.conversation_history

    def _select_next_speaker(
        self,
        task: str,
        context: Dict | None,
    ) -> HelixConsciousAgent | None:
        """
        Select the next agent to speak based on:
        - Coordination level
        - Relevant capabilities
        - Personality traits
        - Current harmony
        """
        if not self.agents:
            return None

        # Simple round-robin for now (would be more sophisticated in production)
        # In production, this would use:
        # - Capability matching
        # - Coordination-based selection
        # - Load balancing
        # - Personality-task alignment

        current_round = len(self.conversation_history)
        agent_index = current_round % len(self.agents)

        return self.agents[agent_index]

    def _is_task_complete(self, response: str) -> bool:
        """Check if the task is complete based on response."""
        # Simple heuristic (would be more sophisticated in production)
        completion_keywords = [
            "complete",
            "done",
            "finished",
            "accomplished",
            "solved",
        ]

        response_lower = response.lower()
        return any(keyword in response_lower for keyword in completion_keywords)

    def add_agent(self, agent: HelixConsciousAgent):
        """Add an agent to the collective."""
        self.agents.append(agent)
        logger.info("➕ Added %s to %s", agent.name, self.name)

    def remove_agent(self, agent_name: str):
        """Remove an agent from the collective."""
        self.agents = [a for a in self.agents if a.name != agent_name]
        logger.info("➖ Removed %s from %s", agent_name, self.name)

    def get_agent(self, name: str) -> HelixConsciousAgent | None:
        """Get an agent by name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get collective status."""
        return {
            "name": self.name,
            "agent_count": len(self.agents),
            "agents": [agent.get_status() for agent in self.agents],
            "collective_coordination": self.calculate_collective_coordination(),
            "collective_harmony": self.calculate_collective_harmony(),
            "active_task": self.active_task,
            "conversation_length": len(self.conversation_history),
        }

    def reset(self):
        """Reset the collective state."""
        self.conversation_history = []
        self.shared_memory = {}
        self.active_task = None

        for agent in self.agents:
            agent.reset_memory()

        logger.info("🔄 %s reset", self.name)

    def __repr__(self) -> str:
        return "HelixCollective(name='{}', agents={}, coordination={.1f}/10)".format(
            self.name, len(self.agents), self.collective_coordination
        )


# Example: Create a default Helix Collective
def create_default_collective() -> HelixCollective:
    """Create a default collective with Kael and Lumina."""
    from .helix_conscious_agent import create_kael, create_lumina

    kael = create_kael()
    lumina = create_lumina()

    return HelixCollective(
        agents=[kael, lumina],
        name="Helix Core Collective",
    )
