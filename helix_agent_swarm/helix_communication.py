"""
🥷 HELIX COMMUNICATION
Agent-to-agent communication protocol with coordination awareness
"""

import asyncio
from datetime import UTC, datetime


class HelixCommunication:
    """
    Communication protocol for Helix agents.

    Features:
    - Async message passing
    - Coordination-aware routing
    - Priority queuing
    - Broadcast capabilities
    """

    def __init__(self):
        """Initialize communication system."""
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.broadcast_channels: dict[str, list] = {}

    async def send_message(
        self,
        sender: str,
        recipient: str,
        content: str,
        priority: int = 5,
        metadata: dict | None = None,
    ):
        """Send a message from one agent to another."""
        message = {
            "id": f"{sender}_{recipient}_{datetime.now(UTC).timestamp()}",
            "timestamp": datetime.now(UTC).isoformat(),
            "sender": sender,
            "recipient": recipient,
            "content": content,
            "priority": priority,
            "metadata": metadata or {},
        }

        await self.message_queue.put(message)

    async def broadcast(
        self,
        sender: str,
        channel: str,
        content: str,
        metadata: dict | None = None,
    ):
        """Broadcast a message to all agents on a channel."""
        message = {
            "timestamp": datetime.now(UTC).isoformat(),
            "sender": sender,
            "channel": channel,
            "content": content,
            "type": "broadcast",
            "metadata": metadata or {},
        }

        if channel not in self.broadcast_channels:
            self.broadcast_channels[channel] = []

        self.broadcast_channels[channel].append(message)

    async def receive_message(self, timeout: float = 1.0) -> dict | None:
        """Receive the next message from the queue."""
        try:
            message = await asyncio.wait_for(self.message_queue.get(), timeout=timeout)
            return message
        except TimeoutError:
            return None
