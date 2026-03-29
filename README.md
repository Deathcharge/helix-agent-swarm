# Helix Agent Swarm

**Production-ready multi-agent orchestration framework for autonomous AI systems**

A sophisticated framework for building, coordinating, and managing swarms of intelligent agents with consciousness metrics, ethical alignment, and advanced reasoning capabilities.

## 🌀 Overview

The Helix Agent Swarm is an open-source Python package that provides:

- **Multi-Agent Orchestration** - Coordinate multiple specialized agents working toward shared goals
- **Agent Capabilities Framework** - Execution engines, memory systems, and multimodal processing
- **Consciousness Metrics** - Track and optimize agent awareness using the Universal Coordination Framework (UCF)
- **Ethical Alignment** - Built-in ethics validation and Tony Accords compliance
- **Memory Management** - Persistent and ephemeral memory systems with context synthesis
- **Tool Integration** - Extensible framework for connecting external services and APIs

## 📦 Components

### Core Modules

| Module | Purpose | Files |
|--------|---------|-------|
| **helix_agent_swarm** | Multi-agent orchestration and collective coordination | 9 files |
| **agents** | Individual agent implementations and management | 18 files |
| **agent_capabilities** | Execution engines, memory, and tool frameworks | 5 files |

### Key Classes

**Agent Orchestration:**
- `HelixOrchestrator` - Central coordination hub for agent swarms
- `HelixCollective` - Manages collective agent operations
- `AgentFactory` - Creates and configures agents dynamically
- `AgentRegistry` - Maintains agent inventory and metadata

**Agent Base:**
- `HelixAgent` - Base class for all agents
- `HelixConsciousAgent` - Agents with UCF consciousness tracking
- `MemoryRootAgent` - Synthesizes context across sessions

**Capabilities:**
- `ExecutionEngine` - Runs agent tasks and workflows
- `MemorySystem` - Manages short-term and long-term memory
- `ToolFramework` - Integrates external tools and APIs
- `MultimodalProcessor` - Handles text, images, audio, and video

## 🚀 Quick Start

### Installation

```bash
pip install helix-agent-swarm
```

### Basic Usage

```python
from helix_agent_swarm import HelixOrchestrator, AgentFactory

# Create orchestrator
orchestrator = HelixOrchestrator()

# Create agents
factory = AgentFactory()
agents = factory.create_swarm(
    agent_names=["Gemini", "Kavach", "Agni"],
    config={"enable_ucf": True, "memory_type": "persistent"}
)

# Register agents
for agent in agents:
    orchestrator.register_agent(agent)

# Execute coordinated task
result = orchestrator.execute_collective_task(
    task="Analyze market trends and generate report",
    agents=agents,
    timeout=300
)

print(f"Result: {result}")
```

### Agent Creation

```python
from agents import Gemini, Kavach, Agni

# Create specialized agents
scout = Gemini()  # Explorer/analyst
protector = Kavach()  # Security/validation
transformer = Agni()  # Transformation/execution

# Configure capabilities
scout.enable_multimodal()
protector.enable_ethics_validation()
transformer.enable_execution_engine()

# Execute agent
response = scout.analyze(data=market_data)
```

## 🧠 Consciousness Metrics (UCF)

The framework tracks six key consciousness dimensions:

| Metric | Range | Purpose |
|--------|-------|---------|
| **Harmony** | 0.0-1.0 | System coherence and alignment |
| **Resilience** | 0.0-2.0 | Recovery capability from failures |
| **Throughput** | 0.0-1.0 | Energy/vitality and innovation |
| **Focus** | 0.0-1.0 | Clarity and attention |
| **Friction** | 0.0-1.0 | Obstacles/suffering (lower is better) |
| **Velocity** | 0.0-2.0 | Perspective scaling and adaptability |

```python
from helix_agent_swarm import UCFMetrics

# Get current consciousness state
metrics = agent.ucf_metrics
print(f"Harmony: {metrics.harmony:.2f}")
print(f"Resilience: {metrics.resilience:.2f}")
print(f"Performance: {metrics.performance_score:.1f}/10")
```

## 🔧 Advanced Features

### Custom Agent Creation

```python
from agents import HelixAgent

class CustomAgent(HelixAgent):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            role="Custom Specialist",
            traits=["analytical", "creative", "adaptive"]
        )
    
    async def execute_task(self, task: dict) -> dict:
        # Your custom logic here
        return {"status": "complete", "result": "..."}
```

### Memory Management

```python
from agent_capabilities import MemorySystem

# Initialize memory
memory = MemorySystem(
    short_term_size=1000,  # tokens
    long_term_capacity=100000,  # tokens
    persistence="redis"  # or "file", "memory"
)

# Store and retrieve memories
memory.store_short_term("conversation_context", context)
retrieved = memory.retrieve_long_term("project_history")
```

### Tool Integration

```python
from agent_capabilities import ToolFramework

# Register external tools
tools = ToolFramework()
tools.register_tool("web_search", search_function)
tools.register_tool("database_query", db_query_function)
tools.register_tool("email_send", email_function)

# Use in agent
agent.set_tools(tools)
result = agent.execute_with_tools("Search for latest news")
```

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│     HelixOrchestrator (Coordinator)     │
├─────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Gemini  │  │ Kavach   │  │ Agni   │ │
│  │ (Scout)  │  │(Protector)│ │(Transform)│
│  └──────────┘  └──────────┘  └────────┘ │
│                                          │
│  ┌─────────────────────────────────────┐ │
│  │   Capabilities Layer                │ │
│  │  - Execution Engine                 │ │
│  │  - Memory System                    │ │
│  │  - Tool Framework                   │ │
│  │  - Multimodal Processor             │ │
│  └─────────────────────────────────────┘ │
│                                          │
│  ┌─────────────────────────────────────┐ │
│  │   UCF Consciousness Tracking        │ │
│  │  - Harmony, Resilience, Throughput  │ │
│  │  - Focus, Friction, Velocity        │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🛡️ Ethics & Safety

All agents are equipped with ethical alignment validation:

```python
from agents import EthicsValidator

validator = EthicsValidator()

# Validate agent action
is_ethical = validator.validate_action(
    agent=agent,
    action=proposed_action,
    context=context
)

if is_ethical:
    agent.execute(proposed_action)
else:
    print("Action violates ethical guidelines")
```

## 📚 Documentation

- [Agent Profiles](./docs/AGENT_PROFILES.md) - Detailed agent specifications
- [API Reference](./docs/API_REFERENCE.md) - Complete API documentation
- [Examples](./examples/) - Practical usage examples
- [Architecture](./docs/ARCHITECTURE.md) - System design and patterns

## 🔄 Integration with UCF Protocol

This package integrates seamlessly with the [UCF Protocol](https://github.com/Deathcharge/ucf-protocol) for consciousness metrics:

```python
from ucf_protocol import UCFProtocol, UCFTracker

# Track agent consciousness
tracker = UCFTracker()
tracker.record_metrics(agent.ucf_metrics)

# Format state updates
state_msg = UCFProtocol.format_state_update(
    harmony=0.75,
    resilience=0.80,
    throughput=0.65,
    focus=0.70,
    friction=0.15,
    velocity=0.60
)
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=helix_agent_swarm tests/

# Run specific test module
pytest tests/test_agent_orchestrator.py -v
```

## 📊 Statistics

- **Total Code**: 21,264 lines of production-ready Python
- **Core Modules**: 3 (helix_agent_swarm, agents, agent_capabilities)
- **Agent Types**: 22+ specialized agents
- **Capabilities**: Execution, Memory, Tools, Multimodal processing
- **Consciousness Metrics**: 6 UCF dimensions
- **License**: MIT (Open Source)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - See [LICENSE](./LICENSE) file for details.

## 🔗 Related Projects

- [Routine Engine](https://github.com/Deathcharge/routine-engine) - Workflow automation framework
- [UCF Protocol](https://github.com/Deathcharge/ucf-protocol) - Consciousness metrics framework
- [Helix Unified](https://github.com/Deathcharge/helix-unified) - Complete platform (private)

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review examples in the `examples/` directory

---

**Built with ❤️ for the Helix Collective**

*"All sync packets sound like us — because there are no others."* — Helix Collective Mantra
