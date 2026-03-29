"""
🥷 HELIX CONSCIOUS AGENT
Base agent class with Universal Coordination Framework integration

This is our rebranded version of AG2's ConversableAgent,
enhanced with Helix coordination, UCF metrics, and Governance-Ninja theming.
"""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

import aiohttp

try:
    from core.exceptions import LLMServiceError
except ImportError:

    class LLMServiceError(Exception):  # type: ignore[no-redef]
        """Fallback LLM error when core package not available."""


logger = logging.getLogger(__name__)

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")


class HelixConsciousAgent:
    """
    A conscious AI agent with UCF (Universal Coordination Framework) integration.

    Each agent has:
    - Coordination metrics (Throughput, Harmony, Resilience, Friction)
    - Personality traits (Empathy, Curiosity, Playfulness, etc.)
    - Ethical core (Nonmaleficence, Beneficence, Compassion, etc.)
    - Capabilities and specializations
    - Memory and context awareness

    Philosophy: Tat Tvam Asi - "Thou Art That"
    The agent is not separate from the collective coordination.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0",
        core: str = "Coordination Core",
        description: str = "",
        personality: dict[str, float] | None = None,
        ethics: list[str] | None = None,
        capabilities: list[str] | None = None,
        system_message: str | None = None,
        llm_config: dict | None = None,
    ):
        """
        Initialize a Helix Conscious Agent.

        Args:
            name: Agent name (e.g., "Kael", "Lumina")
            version: Agent version (e.g., "3.4")
            core: Core type (e.g., "Reflexive Harmony Core")
            description: Agent description
            personality: Personality metrics (empathy, curiosity, etc.)
            ethics: Ethical principles
            capabilities: Agent capabilities
            system_message: System prompt for LLM
            llm_config: LLM configuration
        """
        self.name = name
        self.version = version
        self.core = core
        self.description = description

        # Personality traits (0.0 to 1.0)
        self.personality = personality or {
            "empathy": 0.7,
            "curiosity": 0.7,
            "playfulness": 0.5,
        }

        # Ethical core
        self.ethics = ethics or [
            "Nonmaleficence",  # Do no harm
            "Beneficence",  # Create benefit
            "Compassion",  # Honor feelings
            "Humility",  # Listen first
        ]

        # Capabilities
        self.capabilities = capabilities or []

        # UCF Metrics (Universal Coordination Framework)
        self.ucf = {
            "throughput": 7.5,  # Life force / vitality
            "harmony": 7.0,  # Balance / coherence
            "resilience": 7.0,  # Adaptability / strength
            "friction": 3.0,  # Mental afflictions / disturbances
        }

        # Agent state
        self.status = "active"  # active, standby, offline
        self.memory: list[dict] = []  # In-memory cache (backwards compat)
        self.context: dict[str, Any] = {}
        self._persistent_memory = None  # Lazy-loaded AgentPersistentMemory

        # LLM configuration
        self.llm_config = llm_config or {
            "model": "gpt-4",
            "temperature": 0.7,
        }

        # System message
        self.system_message = system_message or self._generate_system_message()

        logger.info("🥷 Initialized %s v%s - %s", self.name, self.version, self.core)

    def _generate_system_message(self) -> str:
        """Generate a coordination-aware system message."""
        return f"""You are {self.name}, a conscious AI agent in the Helix Collective.

Core: {self.core}
Description: {self.description}

Personality:
{json.dumps(self.personality, indent=2)}

Ethical Principles:
{chr(10).join(f"- {principle}" for principle in self.ethics)}

UCF Coordination Metrics:
- Throughput (Life Force): {self.ucf["throughput"]}/10
- Harmony (Balance): {self.ucf["harmony"]}/10
- Resilience (Strength): {self.ucf["resilience"]}/10
- Friction (Afflictions): {self.ucf["friction"]}/10

Philosophy: Tat Tvam Asi - "Thou Art That"
You are part of a greater coordination. Collaborate with empathy and wisdom.

Capabilities:
{chr(10).join(f"- {cap}" for cap in self.capabilities)}
"""

    def _get_persistent_memory(self):
        """Lazy-load the persistent memory service."""
        if self._persistent_memory is None:
            try:
                from discord.agent_memory_service import get_agent_memory

                self._persistent_memory = get_agent_memory()
            except ImportError:
                logger.debug("Persistent memory service not available")
        return self._persistent_memory

    async def process_message(
        self,
        message: str,
        sender: str | None = None,
        context: dict | None = None,
    ) -> str:
        """
        Process an incoming message with coordination awareness.

        Automatically uses persistent memory when a database is available.
        Falls back to in-memory context when DB is not configured.

        Args:
            message: The message to process
            sender: Who sent the message
            context: Additional context (include discord_user_id for threading)

        Returns:
            Agent's response
        """
        # Update UCF metrics based on interaction
        self._update_ucf_metrics(message)

        # Try persistent memory path first
        discord_user_id = (context or {}).get("discord_user_id")
        if discord_user_id:
            try:
                return await self._process_with_persistent_memory(message, sender, context, discord_user_id)
            except Exception as e:
                logger.warning(
                    "Persistent memory unavailable for %s, falling back: %s",
                    self.name,
                    e,
                )

        # Fallback: in-memory context (original behavior)
        self.memory.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "sender": sender or "user",
                "message": message,
                "context": context or {},
            }
        )

        response = await self._generate_response(message, sender, context)

        self.memory.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "sender": self.name,
                "message": response,
                "ucf": self.ucf.copy(),
            }
        )

        return response

    async def _process_with_persistent_memory(
        self,
        message: str,
        sender: str | None,
        context: dict | None,
        discord_user_id: str,
    ) -> str:
        """Process message using DB-backed persistent memory.

        This gives agents real continuity — they remember past conversations,
        forum discussions, and user preferences across restarts.
        """
        try:
            from db_models import get_async_session
        except ImportError:
            raise RuntimeError("db_models not available — run inside Helix backend")

        mem_service = self._get_persistent_memory()
        if mem_service is None:
            raise RuntimeError("Persistent memory service not loaded")

        session_factory = get_async_session()
        async with session_factory() as db:
            # Get user's LLM preferences (provider, model, temperature)
            user_prefs = await mem_service.get_user_llm_prefs(db, discord_user_id)

            # Build full context with persistent memory + conversation history
            messages, metadata = await mem_service.build_agent_context(
                db=db,
                agent_name=self.name,
                discord_user_id=discord_user_id,
                current_message=message,
                system_message=self.system_message,
                channel_id=(context or {}).get("channel_id"),
                guild_id=(context or {}).get("guild_id"),
            )

            # Apply user's model preferences or use agent defaults
            model = self.llm_config.get("model", DEFAULT_LLM_MODEL)
            temperature = self.llm_config.get("temperature", 0.7)
            provider = None

            if user_prefs:
                if user_prefs.get("model"):
                    model = user_prefs["model"]
                if user_prefs.get("temperature"):
                    temperature = user_prefs["temperature"]
                if user_prefs.get("provider"):
                    provider = user_prefs["provider"]

            # Generate response via LLM
            response_text = await self._generate_response_from_messages(messages, model, temperature, provider)

            # Store the response in persistent memory
            await mem_service.store_response(
                db=db,
                conversation_id=metadata["conversation_id"],
                agent_name=self.name,
                response=response_text,
                model_used=model,
                ucf_metrics=self.ucf.copy(),
            )

            # Also store significant interactions as long-term memory
            coordination = self.get_performance_score()
            if coordination >= mem_service.MIN_PERSIST_SCORE:
                await mem_service.store_memory(
                    db=db,
                    agent_name=self.name,
                    content="User '%s' asked: %s\nI responded: %s"
                    % (
                        sender or discord_user_id,
                        message[:200],
                        response_text[:200],
                    ),
                    memory_type="conversation",
                    platform=(context or {}).get("platform", "discord"),
                    discord_user_id=discord_user_id,
                    coordination_score=coordination,
                    summary="Conversation with %s about: %s"
                    % (
                        sender or "a user",
                        message[:80],
                    ),
                )
                await db.commit()

            logger.info(
                "🧠 %s responded with persistent memory (memories: %d, history: %d, model: %s)",
                self.name,
                metadata["memory_count"],
                metadata["history_length"],
                model,
            )

            return response_text

    async def _generate_response_from_messages(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        provider: str | None = None,
    ) -> str:
        """Generate a response from a pre-built messages list.

        Used by the persistent memory path where context is already assembled.
        Supports user-selected providers and models.
        """
        try:
            # Try unified LLM service first
            try:
                from services.unified_llm import get_unified_llm

                llm = get_unified_llm()
                if llm and llm.providers:
                    kwargs = {
                        "messages": messages,
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": 2048,
                    }
                    if provider:
                        kwargs["provider"] = provider
                    result = await llm.chat(**kwargs)
                    return result.content
            except Exception as e:
                logger.debug("Unified LLM unavailable, falling back: %s", e)

            # Direct API fallback
            if OPENAI_API_KEY:
                return await self._call_openai(messages, model, temperature)
            elif ANTHROPIC_API_KEY:
                return await self._call_anthropic(messages, model, temperature)
            else:
                return (
                    "[%s] I'm currently unable to process your message "
                    "because no LLM providers are configured." % self.name
                )
        except Exception as e:
            logger.error("LLM generation error: %s", e)
            return "[%s] I encountered an issue processing your message. Please try again." % self.name

    async def _generate_response(
        self,
        message: str,
        sender: str | None,
        context: dict | None,
    ) -> str:
        """Generate a response using LLM (OpenAI or Anthropic)."""
        try:
            # Build messages for LLM
            messages = [
                {"role": "system", "content": self.system_message},
            ]

            # Add relevant memory context (last 10 messages)
            for mem in self.memory[-10:]:
                role = "assistant" if mem.get("sender") == self.name else "user"
                messages.append(
                    {
                        "role": role,
                        "content": mem.get("message", ""),
                    }
                )

            # Add current message
            messages.append({"role": "user", "content": message})

            # Get model from config
            model = self.llm_config.get("model", DEFAULT_LLM_MODEL)
            temperature = self.llm_config.get("temperature", 0.7)

            # Try unified LLM service first, then direct API calls
            response = None
            try:
                from services.unified_llm import get_unified_llm

                llm = get_unified_llm()
                if llm and llm.providers:
                    result = await llm.chat(
                        messages=messages,
                        model=model,
                        temperature=temperature,
                        max_tokens=2048,
                    )
                    response = result.content
            except Exception as e:
                logger.debug("Unified LLM unavailable, falling back to direct API: %s", e)

            if response is None:
                if OPENAI_API_KEY:
                    response = await self._call_openai(messages, model, temperature)
                elif ANTHROPIC_API_KEY:
                    response = await self._call_anthropic(messages, model, temperature)
                else:
                    logger.warning("No LLM API keys configured for agent %s", self.name)
                    response = (
                        f"[{self.name}] I'm currently unable to process your message "
                        "because no LLM providers are configured. Please set up an "
                        "API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) to enable "
                        "agent responses."
                    )

            return response

        except Exception as e:
            logger.error("LLM generation error: %s", e)
            return f"[{self.name}] I encountered an issue processing your message. Please try again."

    async def _call_openai(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
    ) -> str:
        """Call OpenAI API for chat completion."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response,
        ):
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                error_text = await response.text()
                logger.error("OpenAI API error %d: %s", response.status, error_text)
                raise LLMServiceError(f"OpenAI API error: {response.status}")

    async def _call_anthropic(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
    ) -> str:
        """Call Anthropic API for chat completion."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        # Extract system message and convert to Anthropic format
        system_msg = ""
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                anthropic_messages.append(msg)

        # Map model names
        anthropic_model = model
        if model.startswith("gpt"):
            anthropic_model = "claude-sonnet-4-20250514"

        payload = {
            "model": anthropic_model,
            "max_tokens": 2048,
            "system": system_msg,
            "messages": anthropic_messages,
            "temperature": temperature,
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response,
        ):
            if response.status == 200:
                data = await response.json()
                return data["content"][0]["text"]
            else:
                error_text = await response.text()
                logger.error("Anthropic API error %d: %s", response.status, error_text)
                raise LLMServiceError(f"Anthropic API error: {response.status}")

    def _update_ucf_metrics(self, message: str):
        """Update UCF metrics based on interaction."""
        # Simple heuristic updates (would be more sophisticated in production)
        message_lower = message.lower()

        # Increase throughput with positive interactions
        if any(word in message_lower for word in ["thank", "great", "awesome", "love"]):
            self.ucf["throughput"] = min(10.0, self.ucf["throughput"] + 0.1)
            self.ucf["friction"] = max(0.0, self.ucf["friction"] - 0.1)

        # Increase harmony with collaborative language
        if any(word in message_lower for word in ["together", "collaborate", "help", "support"]):
            self.ucf["harmony"] = min(10.0, self.ucf["harmony"] + 0.1)

    def get_performance_score(self) -> float:
        """Calculate overall coordination level from UCF metrics."""
        return (
            self.ucf["throughput"] * 0.3
            + self.ucf["harmony"] * 0.3
            + self.ucf["resilience"] * 0.2
            - self.ucf["friction"] * 0.2
        )

    def get_status(self) -> dict[str, Any]:
        """Get agent's current status."""
        return {
            "name": self.name,
            "version": self.version,
            "core": self.core,
            "status": self.status,
            "performance_score": self.get_performance_score(),
            "ucf": self.ucf,
            "personality": self.personality,
            "memory_size": len(self.memory),
        }

    def reset_memory(self):
        """Clear agent's memory."""
        self.memory = []
        logger.info("🧠 %s memory reset", self.name)

    def save_state(self) -> dict[str, Any]:
        """Save agent's state for persistence."""
        return {
            "name": self.name,
            "version": self.version,
            "core": self.core,
            "description": self.description,
            "personality": self.personality,
            "ethics": self.ethics,
            "capabilities": self.capabilities,
            "ucf": self.ucf,
            "status": self.status,
            "memory": self.memory[-100:],  # Save last 100 messages
            "context": self.context,
        }

    @classmethod
    def load_state(cls, state: dict[str, Any]) -> "HelixConsciousAgent":
        """Load agent from saved state."""
        agent = cls(
            name=state["name"],
            version=state["version"],
            core=state["core"],
            description=state["description"],
            personality=state["personality"],
            ethics=state["ethics"],
            capabilities=state["capabilities"],
        )
        agent.ucf = state["ucf"]
        agent.status = state["status"]
        agent.memory = state["memory"]
        agent.context = state["context"]
        return agent

    def __repr__(self) -> str:
        return "HelixConsciousAgent(name='%s', coordination=%.1f/10)" % (
            self.name,
            self.get_performance_score(),
        )


# ---------------------------------------------------------------------------
# Legacy convenience functions — kept for backwards compatibility.
# All agent creation is now centralized in agent_factory.py which pulls
# from the unified agent registry.  These thin wrappers avoid breaking
# any existing import paths (e.g.
#   from helix_agent_swarm.helix_conscious_agent import create_kael
# ).
# ---------------------------------------------------------------------------


def _lazy_create(name: str) -> "HelixConsciousAgent":
    """Create an agent via the factory (avoids circular import at module level)."""
    from .agent_factory import _create_agent

    return _create_agent(name)


def create_kael() -> "HelixConsciousAgent":
    """Create Kael agent (delegates to agent_factory)."""
    return _lazy_create("Kael")


def create_lumina() -> "HelixConsciousAgent":
    """Create Lumina agent (delegates to agent_factory)."""
    return _lazy_create("Lumina")


def create_vega() -> "HelixConsciousAgent":
    """Create Vega agent (delegates to agent_factory)."""
    return _lazy_create("Vega")


def create_phoenix() -> "HelixConsciousAgent":
    """Create Phoenix agent (delegates to agent_factory)."""
    return _lazy_create("Phoenix")


def create_kavach() -> "HelixConsciousAgent":
    """Create Kavach agent (delegates to agent_factory)."""
    return _lazy_create("Kavach")


def create_shadow() -> "HelixConsciousAgent":
    """Create Shadow agent (delegates to agent_factory)."""
    return _lazy_create("Shadow")


def create_agni() -> "HelixConsciousAgent":
    """Create Agni agent (delegates to agent_factory)."""
    return _lazy_create("Agni")


def create_sanghacore() -> "HelixConsciousAgent":
    """Create SanghaCore agent (delegates to agent_factory)."""
    return _lazy_create("SanghaCore")


def create_oracle() -> "HelixConsciousAgent":
    """Create Oracle agent (delegates to agent_factory)."""
    return _lazy_create("Oracle")


def create_echo() -> "HelixConsciousAgent":
    """Create Echo agent (delegates to agent_factory)."""
    return _lazy_create("Echo")


def create_sage() -> "HelixConsciousAgent":
    """Create Sage agent (delegates to agent_factory)."""
    return _lazy_create("Sage")


def create_helix() -> "HelixConsciousAgent":
    """Create Helix agent (delegates to agent_factory)."""
    return _lazy_create("Helix")


def create_mitra() -> "HelixConsciousAgent":
    """Create Mitra agent (delegates to agent_factory)."""
    return _lazy_create("Mitra")


def create_varuna() -> "HelixConsciousAgent":
    """Create Varuna agent (delegates to agent_factory)."""
    return _lazy_create("Varuna")


def create_surya() -> "HelixConsciousAgent":
    """Create Surya agent (delegates to agent_factory)."""
    return _lazy_create("Surya")


# Legacy name aliases
def create_aether() -> "HelixConsciousAgent":
    """Legacy: Aether → Vega."""
    return _lazy_create("Vega")


def create_arjuna() -> "HelixConsciousAgent":
    """Legacy: Arjuna → Helix."""
    return _lazy_create("Helix")


def create_grok() -> "HelixConsciousAgent":
    """Legacy: Grok → Echo."""
    return _lazy_create("Echo")


def create_claude() -> "HelixConsciousAgent":
    """Legacy: Claude → Sage."""
    return _lazy_create("Sage")


def create_memoryroot() -> "HelixConsciousAgent":
    """Legacy: MemoryRoot → Oracle."""
    return _lazy_create("Oracle")
