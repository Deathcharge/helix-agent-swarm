"""
🥷 HELIX AGENT SWARM API ROUTES
FastAPI routes for multi-agent system
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

try:
    from saas.guards import require_pro
except ImportError:
    require_pro = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

from .helix_orchestrator import get_orchestrator

# Agent Swarm requires PRO tier or higher
_deps = [Depends(require_pro)] if require_pro else []
router = APIRouter(prefix="/api/agent-swarm", tags=["Agent Swarm"], dependencies=_deps)


# Request/Response Models
class TaskRequest(BaseModel):
    task: str
    collective_name: str | None = None
    context: dict[str, Any] | None = None


class AgentStatus(BaseModel):
    name: str
    version: str
    core: str
    status: str
    performance_score: float
    ucf: dict[str, float]


class SystemStatus(BaseModel):
    agents: dict[str, Any]
    collectives: dict[str, Any]
    memory: dict[str, Any]
    system_coordination: float
    active_tasks: int


# Routes
@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get complete system status."""
    orchestrator = get_orchestrator()
    return orchestrator.get_system_status()


@router.get("/agents")
async def list_agents():
    """List all registered agents."""
    orchestrator = get_orchestrator()
    return {"agents": [agent.get_status() for agent in orchestrator.agents.values()]}


@router.get("/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get specific agent details."""
    orchestrator = get_orchestrator()

    if agent_name not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = orchestrator.agents[agent_name]
    return agent.get_status()


@router.get("/collectives")
async def list_collectives():
    """List all collectives."""
    orchestrator = get_orchestrator()
    return {"collectives": [collective.get_status() for collective in orchestrator.collectives.values()]}


@router.get("/collectives/{collective_name}")
async def get_collective(collective_name: str):
    """Get specific collective details."""
    orchestrator = get_orchestrator()

    if collective_name not in orchestrator.collectives:
        raise HTTPException(status_code=404, detail="Collective not found")

    collective = orchestrator.collectives[collective_name]
    return collective.get_status()


@router.post("/execute")
async def execute_task(request: TaskRequest):
    """Execute a task using the agent swarm."""
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.create_collective_task(
            task=request.task,
            collective_name=request.collective_name,
            context=request.context,
        )
        return result
    except Exception as e:
        logger.error("Agent swarm task execution failed: %s", e)
        raise HTTPException(status_code=500, detail="Agent swarm task execution failed")


@router.get("/coordination")
async def get_coordination_metrics():
    """Get system-wide coordination metrics."""
    orchestrator = get_orchestrator()

    agents_coordination = {name: agent.get_performance_score() for name, agent in orchestrator.agents.items()}

    collectives_coordination = {
        name: collective.calculate_collective_coordination() for name, collective in orchestrator.collectives.items()
    }

    return {
        "system_coordination": orchestrator.calculate_system_coordination(),
        "agents": agents_coordination,
        "collectives": collectives_coordination,
    }


@router.post("/agents/{agent_name}/message")
async def send_message_to_agent(agent_name: str, message: str):
    """Send a message to a specific agent."""
    orchestrator = get_orchestrator()

    if agent_name not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = orchestrator.agents[agent_name]
    response = await agent.process_message(message, sender="user")

    return {
        "agent": agent_name,
        "response": response,
        "coordination": agent.get_performance_score(),
    }


@router.get("/memory/stats")
async def get_memory_stats():
    """Get memory system statistics."""
    orchestrator = get_orchestrator()
    return orchestrator.memory.get_stats()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    orchestrator = get_orchestrator()
    return {
        "status": "healthy",
        "agents_count": len(orchestrator.agents),
        "collectives_count": len(orchestrator.collectives),
        "system_coordination": orchestrator.calculate_system_coordination(),
    }
