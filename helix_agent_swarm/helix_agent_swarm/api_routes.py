"""
🥷 HELIX AGENT SWARM API ROUTES
FastAPI routes for multi-agent system
"""

import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .helix_orchestrator import get_orchestrator, save_orchestrator

logger = logging.getLogger(__name__)

try:
    from apps.backend.saas.guards import require_pro
except ImportError:
    logger.warning("Could not import require_pro guard — agent swarm routes will fail closed")

    async def require_pro():
        """Fallback guard that rejects all requests when tier guard is unavailable."""
        raise HTTPException(status_code=503, detail="Subscription service unavailable")


try:
    from apps.backend.saas.utils.dependencies import get_current_user
except ImportError:

    async def get_current_user():  # type: ignore[misc]
        """Fallback that rejects when auth import is unavailable."""
        raise HTTPException(status_code=503, detail="Auth service unavailable")


# Agent Swarm requires PRO tier or higher
_deps = [Depends(require_pro)]
router = APIRouter(prefix="/api/agent-swarm", tags=["Agent Swarm"], dependencies=_deps)


def _caller_user_id(user: Any) -> str | None:
    """Extract a stable caller id from ORM-style or dict auth payloads."""
    if user is None:
        return None
    if isinstance(user, dict):
        user_id = user.get("id") or user.get("user_id") or user.get("sub")
    else:
        user_id = getattr(user, "id", None) or getattr(user, "user_id", None) or getattr(user, "sub", None)
    return str(user_id) if user_id else None


def _apply_caller_context(context: dict[str, Any], current_user: Any) -> str | None:
    """Seed mutable swarm calls with stable caller identity and persistence hints."""
    caller_user_id = _caller_user_id(current_user)
    if caller_user_id:
        context.setdefault("caller_user_id", caller_user_id)
        context.setdefault("discord_user_id", caller_user_id)
        context.setdefault("platform", "api")
    return caller_user_id


async def _resolve_orchestrator(current_user: Any = None):
    """Resolve a caller-scoped Redis-backed orchestrator when user identity is available."""
    return await get_orchestrator(_caller_user_id(current_user))


async def _persist_orchestrator(current_user: Any, orchestrator) -> None:
    """Persist mutable swarm state after route-level writes."""
    await save_orchestrator(_caller_user_id(current_user), orchestrator)


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
async def get_system_status(current_user: Any = Depends(get_current_user)):
    """Get complete system status."""
    orchestrator = await _resolve_orchestrator(current_user)
    return orchestrator.get_system_status()


@router.get("/agents")
async def list_agents(current_user: Any = Depends(get_current_user)):
    """List all registered agents."""
    orchestrator = await _resolve_orchestrator(current_user)
    return {"agents": [agent.get_status() for agent in orchestrator.agents.values()]}


@router.get("/agents/{agent_name}")
async def get_agent(agent_name: str, current_user: Any = Depends(get_current_user)):
    """Get specific agent details."""
    orchestrator = await _resolve_orchestrator(current_user)

    if agent_name not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = orchestrator.agents[agent_name]
    return agent.get_status()


@router.get("/collectives")
async def list_collectives(current_user: Any = Depends(get_current_user)):
    """List all collectives."""
    orchestrator = await _resolve_orchestrator(current_user)
    return {"collectives": [collective.get_status() for collective in orchestrator.collectives.values()]}


@router.get("/collectives/{collective_name}")
async def get_collective(
    collective_name: str,
    current_user: Any = Depends(get_current_user),
):
    """Get specific collective details."""
    orchestrator = await _resolve_orchestrator(current_user)

    if collective_name not in orchestrator.collectives:
        raise HTTPException(status_code=404, detail="Collective not found")

    collective = orchestrator.collectives[collective_name]
    return collective.get_status()


@router.post("/execute")
async def execute_task(
    request: TaskRequest,
    current_user: Any = Depends(get_current_user),
):
    """Execute a task using the agent swarm."""
    orchestrator = await _resolve_orchestrator(current_user)
    context = dict(request.context or {})

    caller_user_id = _apply_caller_context(context, current_user)
    task_record = None
    if caller_user_id:
        task_record = {
            "task": request.task,
            "collective_name": request.collective_name,
            "status": "running",
            "started_at": datetime.now(UTC).isoformat(),
        }
        orchestrator.active_tasks.append(task_record)
        await _persist_orchestrator(current_user, orchestrator)

    try:
        result = await orchestrator.execute_task(
            task=request.task,
            collective_name=request.collective_name,
            context=context or None,
        )
        return result
    except Exception as e:
        logger.error("Agent swarm task execution failed: %s", e)
        raise HTTPException(status_code=500, detail="Agent swarm task execution failed") from e
    finally:
        if task_record is not None:
            orchestrator.active_tasks = [task for task in orchestrator.active_tasks if task is not task_record]
        await _persist_orchestrator(current_user, orchestrator)


@router.get("/coordination")
async def get_coordination_metrics(current_user: Any = Depends(get_current_user)):
    """Get system-wide coordination metrics."""
    orchestrator = await _resolve_orchestrator(current_user)

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
async def send_message_to_agent(
    agent_name: str,
    message: str,
    current_user: Any = Depends(get_current_user),
):
    """Send a message to a specific agent."""
    orchestrator = await _resolve_orchestrator(current_user)

    if agent_name not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = orchestrator.agents[agent_name]
    context: dict[str, Any] = {}
    caller_user_id = _apply_caller_context(context, current_user)
    sender = f"user:{caller_user_id}" if caller_user_id else "user"
    response = await agent.process_message(message, sender=sender, context=context or None)
    await _persist_orchestrator(current_user, orchestrator)

    return {
        "agent": agent_name,
        "response": response,
        "coordination": agent.get_performance_score(),
    }


@router.get("/memory/stats")
async def get_memory_stats(current_user: Any = Depends(get_current_user)):
    """Get memory system statistics."""
    orchestrator = await _resolve_orchestrator(current_user)
    return orchestrator.memory.get_stats()


@router.get("/health")
async def health_check(current_user: Any = Depends(get_current_user)):
    """Health check endpoint."""
    orchestrator = await _resolve_orchestrator(current_user)
    return {
        "status": "healthy",
        "agents_count": len(orchestrator.agents),
        "collectives_count": len(orchestrator.collectives),
        "system_coordination": orchestrator.calculate_system_coordination(),
    }
