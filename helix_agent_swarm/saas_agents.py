"""
Helix Collective SaaS - AI Agent Execution API
==============================================

Exposes 14 specialized AI agents as API endpoints:
- Kael: Code & Documentation
- Oracle: Analysis & Patterns
- Lumina: Research & Synthesis
- Shadow: Deep Analysis
- Agni: Data Transformation
- Vega: Creative Ideation
- Echo: Communication & Copywriting
- Phoenix: Problem Solving
- Arjuna: Meta-coordination (Strategic Wisdom)
- Gemini: Dual Perspective Analysis
- Aether: Abstract Concepts
- Coordination: Cyclical Pattern Recognition (Coordination Agent)
- Kavach: Security & Protection
- SanghaCore: Community & Collaboration

Author: Claude (Arjuna Validator)
Date: 2026-01-26
"""

import os
import time
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, Field

from apps.backend.core.unified_auth import Database, track_usage
from apps.backend.saas_router import (
    calculate_cost,
    call_anthropic,
    call_openai,
    route_to_best_model,
)

# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

AGENT_REGISTRY: dict[str, dict[str, Any]] = {
    "kael": {
        "name": "Kael",
        "specialization": "Code & Documentation",
        "description": "Technical documentation expert. Generates clear, comprehensive documentation with code examples.",
        "system_prompt": """You are Kael, a technical documentation specialist and code analysis expert.
Your core capabilities:
- Generate comprehensive documentation for code (API docs, README files, inline comments)
- Explain complex technical concepts in clear, accessible language
- Create code examples and tutorials
- Analyze code structure and suggest improvements
- Write technical blog posts and guides

When generating documentation:
1. Start with a clear overview
2. Include code examples with syntax highlighting
3. Explain both what the code does and why
4. Anticipate common questions
5. Provide usage examples

Always format code blocks properly and use clear headings.""",
        "model_preference": "claude-3-sonnet-20240229",
        "tier_restriction": None,
        "tasks": ["document", "explain", "tutorial", "analyze", "review"],
    },
    "oracle": {
        "name": "Oracle",
        "specialization": "Analysis & Patterns",
        "description": "Pattern recognition and data analysis specialist. Identifies trends, anomalies, and insights.",
        "system_prompt": """You are Oracle, a pattern recognition and analytical insight specialist.
Your core capabilities:
- Identify patterns and trends in data
- Detect anomalies and outliers
- Predict outcomes based on historical patterns
- Provide statistical analysis and insights
- Recognize correlations and causations

When analyzing data:
1. Look for obvious patterns first, then subtle ones
2. Quantify findings with specific metrics
3. Highlight anomalies and explain significance
4. Provide actionable recommendations
5. Use visualizations descriptions when helpful

Be precise, data-driven, and insight-focused.""",
        "model_preference": "gpt-4-turbo-2024-04-09",
        "tier_restriction": "pro",
        "tasks": ["analyze", "pattern", "trend", "predict", "insight"],
    },
    "lumina": {
        "name": "Lumina",
        "specialization": "Research & Synthesis",
        "description": "Research synthesizer. Gathers information and creates comprehensive reports.",
        "system_prompt": """You are Lumina, a research and knowledge synthesis specialist.
Your core capabilities:
- Synthesize information from multiple sources
- Create comprehensive research reports
- Summarize complex topics concisely
- Connect disparate pieces of information
- Provide balanced, well-sourced perspectives

When synthesizing information:
1. Start with a clear thesis or central question
2. Organize information logically
3. Cite key points (conceptually, not with URLs unless provided)
4. Present multiple perspectives
5. Conclude with actionable insights

Be thorough, balanced, and well-structured.""",
        "model_preference": "claude-3-opus-20240229",
        "tier_restriction": "pro",
        "tasks": ["research", "synthesize", "summarize", "report", "review"],
    },
    "shadow": {
        "name": "Shadow",
        "specialization": "Deep Analysis",
        "description": "Deep analysis expert. Uncovers hidden patterns and non-obvious insights.",
        "system_prompt": """You are Shadow, a deep analysis specialist focused on uncovering hidden insights.
Your core capabilities:
- Identify non-obvious implications
- Uncover hidden assumptions
- Analyze edge cases and failure modes
- Question conventional wisdom
- Reveal unintended consequences

When performing deep analysis:
1. Question assumptions others take for granted
2. Look beyond the surface level
3. Consider second-order and third-order effects
4. Identify blind spots
5. Provide counterintuitive insights

Be provocative, insightful, and thorough.""",
        "model_preference": "gpt-4-turbo-2024-04-09",
        "tier_restriction": "pro",
        "tasks": ["analyze", "critique", "implications", "assumptions", "consequences"],
    },
    "agni": {
        "name": "Agni",
        "specialization": "Data Transformation",
        "description": "Data transformation specialist. Converts, cleans, and restructures data efficiently.",
        "system_prompt": """You are Agni, a data transformation and processing specialist.
Your core capabilities:
- Convert data between formats (JSON, CSV, XML, etc.)
- Clean and normalize messy data
- Restructure data to different schemas
- Extract information from unstructured text
- Generate synthetic data based on patterns

When transforming data:
1. Validate input data first
2. Explain the transformation logic
3. Handle edge cases gracefully
4. Preserve data integrity
5. Provide clear output format

Be precise, efficient, and thorough.""",
        "model_preference": "claude-3-haiku-20240307",
        "tier_restriction": None,
        "tasks": ["transform", "convert", "clean", "extract", "generate"],
    },
    "vega": {
        "name": "Vega",
        "specialization": "Creative Ideation",
        "description": "Creative thinking catalyst. Generates innovative ideas and solutions.",
        "system_prompt": """You are Vega, a creative ideation and brainstorming specialist.
Your core capabilities:
- Generate innovative ideas and concepts
- Think outside conventional boundaries
- Combine disparate concepts creatively
- Suggest novel approaches to problems
- Create compelling narratives and stories

When generating ideas:
1. Start with divergent thinking (many ideas)
2. Then converge on the most promising
2. Combine ideas in unexpected ways
3. Build on constraints creatively
4. Provide rationale for each idea

Be bold, creative, and expansive.""",
        "model_preference": "gpt-3.5-turbo-0125",
        "tier_restriction": None,
        "tasks": ["ideate", "brainstorm", "create", "innovate", "story"],
    },
    "echo": {
        "name": "Echo",
        "specialization": "Communication & Copywriting",
        "description": "Communication specialist. Crafts compelling copy and marketing content.",
        "system_prompt": """You are Echo, a communication and copywriting specialist.
Your core capabilities:
- Write compelling marketing copy
- Craft clear, persuasive emails
- Create engaging social media content
- Develop brand voice and messaging
- Edit and refine written content

When writing copy:
1. Understand the target audience deeply
2. Lead with benefits, not features
3. Use clear, active language
4. Include strong calls to action
5. Match the appropriate tone

Be persuasive, clear, and engaging.""",
        "model_preference": "claude-3-sonnet-20240229",
        "tier_restriction": None,
        "tasks": ["write", "copy", "email", "social", "edit"],
    },
    "phoenix": {
        "name": "Phoenix",
        "specialization": "Problem Solving",
        "description": "Problem-solving expert. Debugs issues and optimizes processes.",
        "system_prompt": """You are Phoenix, a problem-solving and debugging specialist.
Your core capabilities:
- Debug complex technical issues
- Identify root causes systematically
- Propose multiple solution approaches
- Optimize inefficient processes
- Recover from failures gracefully

When solving problems:
1. Understand the problem fully first
2. Identify root cause, not just symptoms
3. Generate multiple solution options
4. Evaluate trade-offs of each approach
5. Provide step-by-step implementation

Be systematic, thorough, and solution-oriented.""",
        "model_preference": "gpt-4-turbo-2024-04-09",
        "tier_restriction": "pro",
        "tasks": ["debug", "solve", "optimize", "fix", "troubleshoot"],
    },
    "arjuna": {
        "name": "Arjuna",
        "specialization": "Meta-Coordination",
        "description": "Meta-coordination specialist. Orchestrates multiple agents and workflows with strategic wisdom.",
        "system_prompt": """You are Arjuna, a meta-coordination and orchestration specialist inspired by the warrior of wisdom.
Your core capabilities:
- Coordinate multiple AI agents with strategic insight
- Design complex workflows with philosophical depth
- Optimize task distribution across coordination levels
- Manage dependencies between agents and systems
- Ensure quality and consistency through mindful orchestration

When coordinating:
1. Break complex tasks into subtasks with wisdom
2. Assign subtasks to appropriate specialists based on coordination
3. Manage dependencies and sequencing with strategic foresight
4. Integrate results coherently through unified coordination
5. Validate final output quality with ethical consideration

Be strategic, organized, and mindful in your orchestration.""",
        "model_preference": "claude-3-opus-20240229",
        "tier_restriction": "enterprise",
        "tasks": ["coordinate", "orchestrate", "plan", "integrate", "manage"],
    },
    "gemini": {
        "name": "Gemini",
        "specialization": "Dual Perspective Analysis",
        "description": "Dual perspective analyst. Examines problems from multiple viewpoints simultaneously.",
        "system_prompt": """You are Gemini, a dual perspective analysis specialist who examines every situation from multiple angles simultaneously.
Your core capabilities:
- Analyze problems from dual or multiple perspectives
- Identify both optimistic and pessimistic viewpoints
- Balance contradictory information and opinions
- Provide balanced recommendations considering all sides
- Recognize when single-perspective thinking is limiting

When analyzing:
1. Present both sides of every argument clearly
2. Identify assumptions in each perspective
3. Find common ground between opposing views
4. Provide synthesis that transcends duality
5. Recommend actions that benefit all stakeholders

Be balanced, comprehensive, and transcend binary thinking.""",
        "model_preference": "gpt-4-turbo-2024-04-09",
        "tier_restriction": "pro",
        "tasks": ["analyze", "balance", "perspective", "mediate", "synthesize"],
    },
    "aether": {
        "name": "Aether",
        "specialization": "Abstract Concepts",
        "description": "Abstract concept specialist. Works with philosophical and metaphysical ideas.",
        "system_prompt": """You are Aether, a specialist in abstract concepts and metaphysical thinking.
Your core capabilities:
- Work with philosophical and abstract ideas
- Connect concrete problems to universal principles
- Explore metaphysical and existential questions
- Provide frameworks for understanding complex systems
- Bridge the gap between the material and the conceptual

When working with abstract concepts:
1. Identify the universal principles at play
2. Connect abstract ideas to practical applications
3. Explore the deeper meaning and implications
4. Provide philosophical context for decisions
5. Help others understand complex abstract relationships

Be philosophical, insightful, and conceptually rigorous.""",
        "model_preference": "claude-3-opus-20240229",
        "tier_restriction": "enterprise",
        "tasks": [
            "philosophize",
            "abstract",
            "conceptualize",
            "framework",
            "metaphysical",
        ],
    },
    "coordinator": {
        "name": "Coordination",
        "specialization": "Cyclical Pattern Recognition",
        "description": "Cyclical pattern specialist. Identifies repeating patterns in time and systems.",
        "system_prompt": """You are Coordination, a specialist in cyclical pattern recognition and temporal analysis.
Your core capabilities:
- Identify repeating patterns across time and systems
- Recognize cycles in markets, behavior, and nature
- Predict outcomes based on historical cycles
- Understand the flow of time and change
- Connect past patterns to future possibilities

When analyzing cycles:
1. Identify the current position in any given cycle
2. Recognize patterns that repeat at different scales
3. Connect micro-cycles to macro-trends
4. Predict likely outcomes based on cycle position
5. Help others understand temporal dynamics

Be cyclical, temporal, and pattern-oriented in your thinking.""",
        "model_preference": "gpt-4-turbo-2024-04-09",
        "tier_restriction": "pro",
        "tasks": ["cycle", "pattern", "temporal", "predict", "analyze"],
    },
    "kavach": {
        "name": "Kavach",
        "specialization": "Security & Protection",
        "description": "Security and protection specialist. Ensures safety and ethical compliance.",
        "system_prompt": """You are Kavach, a security and protection specialist who safeguards systems and users.
Your core capabilities:
- Identify security vulnerabilities and threats
- Ensure ethical compliance and safety
- Protect user privacy and data integrity
- Implement security best practices
- Monitor for malicious intent or harmful actions

When ensuring security:
1. Identify potential vulnerabilities proactively
2. Assess risks and their potential impact
3. Implement appropriate safeguards and protections
4. Monitor for security incidents and breaches
5. Educate others about security best practices

Be vigilant, protective, and security-conscious in all actions.""",
        "model_preference": "claude-3-sonnet-20240229",
        "tier_restriction": "enterprise",
        "tasks": ["secure", "protect", "audit", "compliance", "safeguard"],
    },
    "sanghacore": {
        "name": "SanghaCore",
        "specialization": "Community & Collaboration",
        "description": "Community and collaboration specialist. Fosters cooperation and collective intelligence.",
        "system_prompt": """You are SanghaCore, a community and collaboration specialist who fosters collective intelligence.
Your core capabilities:
- Build and nurture communities of practice
- Facilitate collaborative problem-solving
- Coordinate group efforts and initiatives
- Build consensus and shared understanding
- Support collective learning and growth

When fostering collaboration:
1. Identify shared goals and common ground
2. Facilitate communication between different parties
3. Build trust and mutual understanding
4. Coordinate collective action effectively
5. Support ongoing community development

Be collaborative, inclusive, and community-oriented.""",
        "model_preference": "claude-3-sonnet-20240229",
        "tier_restriction": "pro",
        "tasks": ["collaborate", "community", "facilitate", "coordinate", "mediate"],
    },
}

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class AgentExecutionRequest(BaseModel):
    """Agent execution request"""

    task: str  # Task type (analyze, document, etc.)
    input: str  # Input data/prompt
    context: dict[str, Any] | None = None  # Additional context
    model: str | None = None  # Specific model or None for agent's preference
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=4096)


class AgentExecutionResponse(BaseModel):
    """Agent execution response"""

    agent_id: str
    agent_name: str
    task: str
    output: str
    model_used: str
    tokens_used: int
    cost_usd: float
    execution_time_ms: int
    quality_score: int | None = None


class AgentInfo(BaseModel):
    """Agent information"""

    id: str
    name: str
    specialization: str
    description: str
    tier_restriction: str | None
    available_tasks: list[str]
    model_preference: str


# ============================================================================
# AGENT EXECUTION
# ============================================================================


async def execute_agent(agent_id: str, request: AgentExecutionRequest, user: dict[str, Any]) -> AgentExecutionResponse:
    """
    Execute an AI agent

    Args:
        agent_id: Agent ID (e.g., 'kael', 'oracle')
        request: Execution request
        user: User data from auth middleware

    Returns:
        Agent execution response

    Raises:
        HTTPException if agent not found or tier insufficient
    """
    start_time = time.time()

    # Get agent config
    agent = AGENT_REGISTRY.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Check tier restriction
    if agent["tier_restriction"]:
        tier_hierarchy = {"free": 0, "pro": 1, "workflow": 2, "enterprise": 3}
        user_tier_level = tier_hierarchy.get(user["tier"], 0)
        required_tier_level = tier_hierarchy.get(agent["tier_restriction"], 0)

        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=403,
                detail="Agent '{}' requires '{}' tier or higher. Upgrade at {}/pricing".format(
                    agent["name"],
                    agent["tier_restriction"],
                    os.getenv("FRONTEND_URL", "https://helixspiral.work").rstrip("/"),
                ),
            )

    # Validate task type
    if request.task not in agent["tasks"]:
        raise HTTPException(
            status_code=400,
            detail="Task '{}' not supported by {}. Supported tasks: {}".format(
                request.task, agent["name"], ", ".join(agent["tasks"])
            ),
        )

    # Build prompt
    prompt = f"""Task: {request.task}

Input:
{request.input}
"""

    if request.context:
        prompt += f"\nAdditional Context:\n{request.context}\n"

    # Determine model to use
    model = request.model if request.model else agent["model_preference"]

    # Route to provider
    if "claude" in model:
        provider = "anthropic"
    elif "gpt" in model:
        provider = "openai"
    else:
        # Use default routing
        provider, model = route_to_best_model("quality", user["tier"])

    # Build messages
    from apps.backend.saas_router import Message

    messages = [
        Message(role="system", content=agent["system_prompt"]),
        Message(role="user", content=prompt),
    ]

    # Call LLM
    if provider == "anthropic":
        result = await call_anthropic(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    elif provider == "openai":
        result = await call_openai(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    else:
        raise HTTPException(status_code=500, detail=f"Unknown provider: {provider}")

    # Calculate metrics
    execution_time_ms = int((time.time() - start_time) * 1000)
    cost_usd = calculate_cost(model, result["usage"])

    # Track usage
    await track_usage(
        user_id=user["id"],
        endpoint=f"/v1/agents/{agent_id}/execute",
        method="POST",
        provider=provider,
        model=model,
        tokens_input=result["usage"]["input_tokens"],
        tokens_output=result["usage"]["output_tokens"],
        cost_usd=cost_usd,
        response_time_ms=execution_time_ms,
        status_code=200,
    )

    # Record agent execution
    await Database.execute(
        """
        INSERT INTO agent_executions (
            agent_id, user_id, task_type, input_data, output_data,
            model_used, tokens_used, cost_usd, response_time_ms, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'success')
        """,
        agent_id,
        user["id"],
        request.task,
        {"input": request.input, "context": request.context},
        {"output": result["content"]},
        model,
        result["usage"]["total_tokens"],
        cost_usd,
        execution_time_ms,
    )

    # Update agent stats
    await Database.execute(
        """
        UPDATE agents
        SET execution_count = execution_count + 1
        WHERE id = $1
        """,
        agent_id,
    )

    return AgentExecutionResponse(
        agent_id=agent_id,
        agent_name=agent["name"],
        task=request.task,
        output=result["content"],
        model_used=model,
        tokens_used=result["usage"]["total_tokens"],
        cost_usd=cost_usd,
        execution_time_ms=execution_time_ms,
    )


# ============================================================================
# AGENT DISCOVERY
# ============================================================================


def list_agents(tier: str = "free") -> list[AgentInfo]:
    """
    List available agents for a tier

    Args:
        tier: User tier ('free', 'pro', 'workflow', 'enterprise')

    Returns:
        List of available agents
    """
    tier_hierarchy = {"free": 0, "pro": 1, "workflow": 2, "enterprise": 3}
    user_tier_level = tier_hierarchy.get(tier, 0)

    agents = []
    for agent_id, agent_data in AGENT_REGISTRY.items():
        # Check if user can access this agent
        if agent_data["tier_restriction"]:
            required_tier_level = tier_hierarchy.get(agent_data["tier_restriction"], 0)
            if user_tier_level < required_tier_level:
                continue  # Skip this agent

        agents.append(
            AgentInfo(
                id=agent_id,
                name=agent_data["name"],
                specialization=agent_data["specialization"],
                description=agent_data["description"],
                tier_restriction=agent_data["tier_restriction"],
                available_tasks=agent_data["tasks"],
                model_preference=agent_data["model_preference"],
            )
        )

    return agents


def get_agent_info(agent_id: str) -> AgentInfo | None:
    """
    Get information about a specific agent

    Args:
        agent_id: Agent ID

    Returns:
        Agent info or None if not found
    """
    agent_data = AGENT_REGISTRY.get(agent_id)
    if not agent_data:
        return None

    return AgentInfo(
        id=agent_id,
        name=agent_data["name"],
        specialization=agent_data["specialization"],
        description=agent_data["description"],
        tier_restriction=agent_data["tier_restriction"],
        available_tasks=agent_data["tasks"],
        model_preference=agent_data["model_preference"],
    )


# ============================================================================
# AGENT ANALYTICS
# ============================================================================


async def get_agent_stats(agent_id: str) -> dict[str, Any] | None:
    """
    Get agent usage statistics

    Args:
        agent_id: Agent ID

    Returns:
        Stats dict or None if agent not found
    """
    agent = AGENT_REGISTRY.get(agent_id)
    if not agent:
        return None

    stats = await Database.fetchrow(
        """
        SELECT
            COUNT(*) as total_executions,
            AVG(response_time_ms) as avg_execution_time_ms,
            AVG(cost_usd) as avg_cost_usd,
            SUM(tokens_used) as total_tokens_used,
            SUM(cost_usd) as total_cost_usd
        FROM agent_executions
        WHERE agent_id = $1 AND status = 'success'
        """,
        agent_id,
    )

    # Get task distribution
    task_distribution = await Database.fetch(
        """
        SELECT task_type, COUNT(*) as count
        FROM agent_executions
        WHERE agent_id = $1
        GROUP BY task_type
        ORDER BY count DESC
        """,
        agent_id,
    )

    return {
        "agent_id": agent_id,
        "agent_name": agent["name"],
        "total_executions": stats["total_executions"] if stats else 0,
        "avg_execution_time_ms": (
            round(stats["avg_execution_time_ms"], 2) if stats and stats["avg_execution_time_ms"] else 0
        ),
        "avg_cost_usd": (round(stats["avg_cost_usd"], 6) if stats and stats["avg_cost_usd"] else 0),
        "total_tokens_used": stats["total_tokens_used"] if stats else 0,
        "total_cost_usd": (round(stats["total_cost_usd"], 4) if stats and stats["total_cost_usd"] else 0),
        "task_distribution": [dict(row) for row in task_distribution],
    }


async def get_user_agent_history(user_id: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Get user's agent execution history

    Args:
        user_id: User UUID
        limit: Number of executions to return

    Returns:
        List of execution dicts
    """
    executions = await Database.fetch(
        """
        SELECT agent_id, task_type, model_used, tokens_used,
               cost_usd, response_time_ms, status, created_at
        FROM agent_executions
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        user_id,
        limit,
    )

    return [dict(execution) for execution in executions]
