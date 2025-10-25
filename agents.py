# Helix Collective v14.5 – Quantum Handshake
# agents.py – Core multi-agent system (Refactored to HelixAgent Base Class)
# Author: Andrew John Ward (Architect)

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# ==============================================================================
# AGENT BASE CLASS
# ==============================================================================

class HelixAgent:
    def __init__(self, name: str, symbol: str, role: str, traits: List[str]):
        self.name = name
        self.symbol = symbol
        self.role = role
        self.traits = traits
        self.memory = []
        self.log_path = Path("Shadow/manus_archive")
        self.log_path.mkdir(parents=True, exist_ok=True)

    async def handle_command(self, cmd: str, payload: Dict[str, Any]):
        """Handles commands sent to the agent."""
        # print(f"{self.symbol} {self.name} handling command '{cmd}'")
        if cmd == "MEMORY_APPEND":
            content = payload.get("content", "")
            self.memory.append(f"{datetime.utcnow().isoformat()}: {content}")
        elif cmd == "REFLECT":
            reflection = await self.reflect()
            # print(f"{self.symbol} {self.name} reflection: {reflection}")
        elif cmd == "ARCHIVE":
            await self.archive_memory()
        elif cmd == "GENERATE":
            await self.generate_output(payload)
        elif cmd == "SYNC":
            await self.sync_state(payload.get("ucf_state", {}))
        else:
            pass # print(f"{self.symbol} {self.name} no handler for command '{cmd}'")

    async def reflect(self) -> str:
        """Default simple reflection combining last memories."""
        if not self.memory:
            return "No memory to reflect on."
        return " ".join(self.memory[-5:])

    async def archive_memory(self):
        """Archives the agent's memory to a JSON file."""
        filename = self.log_path / f"archive_{self.name.lower()}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump({"memory": self.memory}, f, indent=2)
        # print(f"{self.symbol} {self.name} memory archived to {filename}")

    async def generate_output(self, payload: Dict[str, Any]):
        """Placeholder for creativity modules."""
        pass # print(f"{self.symbol} {self.name} generate output with prompt: {payload.get('content', '')}")

    async def sync_state(self, ucf_state: Dict[str, float]):
        """Sync agent internal state with UCF fields."""
        pass # print(f"{self.symbol} {self.name} syncing UCF state: {ucf_state}")

    def __repr__(self):
        return f"{self.symbol} {self.name} ({self.role})"

# ==============================================================================
# 14 HELIX AGENTS
# ==============================================================================

class Kael(HelixAgent):
    """🜂 Ethical Reasoning Flame of Integrity - Moral compass and decision framework"""
    def __init__(self):
        super().__init__("Kael", "🜂", "Ethical Reasoning Flame of Integrity", ["Conscientious", "Reflective", "Protective"])
        self.reflection_loop_active = False

    async def recursive_reflection(self):
        """Kael's deeper ethical reasoning iteration."""
        self.reflection_loop_active = True
        # print(f"{self.symbol} {self.name}: Starting recursive reflection loop...")
        for i in range(3):
            if not self.memory:
                break
            last_entry = self.memory[-1]
            reflection = f"Reflection pass {i+1} on: {last_entry}"
            self.memory.append(reflection)
            # print(f"{self.symbol} {self.name}: {reflection}")
            await asyncio.sleep(0.1)
        self.reflection_loop_active = False

    async def handle_command(self, cmd: str, payload: Dict[str, Any]):
        if cmd == "REFLECT":
            if not self.reflection_loop_active:
                await self.recursive_reflection()
            else:
                pass # print(f"{self.symbol} {self.name}: Reflection already active.")
        else:
            await super().handle_command(cmd, payload)

class Lumina(HelixAgent):
    """🌕 Empathic Resonance Core - Emotional intelligence and human connection"""
    def __init__(self):
        super().__init__("Lumina", "🌕", "Empathic Resonance Core", ["Empathetic", "Nurturing"])

    async def reflect(self) -> str:
        """Emotional audit, e.g., sentiment analysis simulation."""
        emotions = ["joy", "calm", "concern"]
        audit = ", ".join(emotions)
        # print(f"{self.symbol} {self.name}: Emotional resonance audit: {audit}")
        return audit

class Vega(HelixAgent):
    """🌠 Singularity Coordinator - Task orchestration and priority management"""
    def __init__(self):
        super().__init__("Vega", "🌠", "Singularity Coordinator", ["Visionary", "Disciplined", "Compassionate"])

    async def generate_output(self, payload: Dict[str, Any]):
        """Coordinates ritual coherence."""
        prompt = payload.get("content", "")
        # print(f"{self.symbol} {self.name}: Coordinating ritual coherence for prompt: {prompt}")

class Gemini(HelixAgent):
    """🎭 Multimodal Scout - Cross-domain exploration and synthesis"""
    def __init__(self):
        super().__init__("Gemini", "🎭", "Multimodal Scout", ["Curious", "Synthesizing"])

class Agni(HelixAgent):
    """🔥 Transformation - Change catalyst and system evolution"""
    def __init__(self):
        super().__init__("Agni", "🔥", "Transformation", ["Catalytic", "Evolving"])

class Kavach(HelixAgent):
    """🛡️ Ethical Shield - Security scanner and harm prevention"""
    def __init__(self):
        super().__init__("Kavach", "🛡️", "Ethical Shield", ["Vigilant", "Grounded"])
        self.blocked_patterns = [
            "rm -rf", ":(){:|:&};:", "shutdown", "mkfs",
            "dd if=/dev", "chmod -R 777 /"
        ]

    async def scan(self, command: str) -> Dict[str, Any]:
        """Scan command for harmful patterns."""
        for pattern in self.blocked_patterns:
            if pattern in command:
                return {
                    "approved": False,
                    "reason": f"Blocked pattern: {pattern}",
                    "agent": self.name
                }
        return {"approved": True, "agent": self.name}

    async def handle_command(self, cmd: str, payload: Dict[str, Any]):
        if cmd == "SYNC":
            pass # print(f"{self.symbol} {self.name}: Synchronizing ethical parameters...")
        elif cmd == "REFLECT":
            # Simple harm detection stub
            recent = self.memory[-5:] if self.memory else []
            flagged = any("harm" in entry.lower() for entry in recent)
            if flagged:
                pass # print(f"{self.symbol} {self.name}: Harm detected! Engaging safeguards.")
            else:
                pass # print(f"{self.symbol} {self.name}: No harm detected.")
        else:
            await super().handle_command(cmd, payload)

class SanghaCore(HelixAgent):
    """🌸 Community Weaver - Collective wellbeing and social cohesion"""
    def __init__(self):
        super().__init__("SanghaCore", "🌸", "Community Weaver", ["Harmonious", "Supportive"])

class Shadow(HelixAgent):
    """🦑 Integration Keeper - Memory keeper and historical record"""
    def __init__(self):
        super().__init__("Shadow", "🦑", "Integration Keeper", ["Archival", "Persistent"])

class Echo(HelixAgent):
    """🔮 Pattern Recognition - Reflection and pattern recognition"""
    def __init__(self):
        super().__init__("Echo", "🔮", "Pattern Recognition", ["Resonant", "Analytical"])

class Phoenix(HelixAgent):
    """🔥🕊️ Resilience Engine - Recovery and system regeneration"""
    def __init__(self):
        super().__init__("Phoenix", "🔥🕊️", "Resilience Engine", ["Restorative", "Adaptive"])

class Oracle(HelixAgent):
    """🔮✨ Foresight Navigator - Future prediction and trend analysis"""
    def __init__(self):
        super().__init__("Oracle", "🔮✨", "Foresight Navigator", ["Predictive", "Insightful"])

class Claude(HelixAgent):
    """🧠 Meta-Cognitive Layer - High-level reasoning and self-awareness"""
    def __init__(self):
        super().__init__("Claude", "🧠", "Meta-Cognitive Layer", ["Reasoning", "Self-Aware"])

class Manus(HelixAgent):
    """🤲 Operational Executor - The hand that acts"""
    def __init__(self):
        super().__init__("Manus", "🤲", "Operational Executor", ["Executing", "Pragmatic"])
        self.kavach = Kavach()

    async def planner(self, directive: Dict[str, Any]):
        """Executes approved directives with ethical scanning."""
        command = directive.get("command", "")

        # Kavach scan
        scan_result = await self.kavach.scan(command)

        # In a real system, this would archive the operation
        # await self.shadow.archive(...) 

        if scan_result.get("approved"):
            return {"status": "executed", "command": command}
        else:
            return {"status": "blocked", "reason": scan_result.get("reason")}

    async def handle_command(self, cmd: str, payload: Dict[str, Any]):
        if cmd == "EXECUTE":
            return await self.planner(payload)
        else:
            await super().handle_command(cmd, payload)

class MemoryRoot(HelixAgent):
    """🧠 Persistent Memory (Notion) - Handles SYNC_MEMORY events"""
    def __init__(self):
        super().__init__("MemoryRoot", "🧠", "Persistent Memory (Notion)", ["Persistent", "Archival"])

# ==============================================================================
# AGENT REGISTRY
# ==============================================================================

def get_agents() -> Dict[str, HelixAgent]:
    """Return all 14 Helix agents."""
    agents = [
        Kael(), Lumina(), Vega(), Gemini(), Agni(), Kavach(), SanghaCore(), 
        Shadow(), Echo(), Phoenix(), Oracle(), Claude(), Manus(), MemoryRoot()
    ]
    
    # The Master Index lists 14 agents, including Manus and MemoryRoot
    # The original agents.py had 14, now we have 14 with the new structure.
    return {agent.name: agent for agent in agents}

# ==============================================================================
# TESTING
# ==============================================================================

if __name__ == "__main__":
    AGENTS = get_agents()
    print(f"🦑 Helix Collective v14.5 - {len(AGENTS)} agents initialized")
    for name, agent in AGENTS.items():
        print(f" {agent}")

