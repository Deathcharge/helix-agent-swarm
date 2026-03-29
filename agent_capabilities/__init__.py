"""
Helix Agent Capabilities Package
================================
Advanced capabilities for Helix Collective agents including:
- Code execution (Python, JavaScript, Shell)
- File system operations
- Web browsing and search
- Terminal commands
- Tool-use framework
- Memory and context management
- Multi-modal processing

This package makes Helix agents as capable as Claude Code, Grok, or other
advanced AI coding assistants.
"""

from .execution_engine import (
    AgentExecutionEngine,
    AgentWorkspace,
    ExecutionLanguage,
    ExecutionResult,
    FileOperations,
    SecureSandbox,
    ToolCall,
    ToolType,
    WebOperations,
    browse_url,
    execute_code,
    get_execution_engine,
    web_search,
)

try:
    from .memory_system import (
        AgentMemory,
        ConversationHistory,
        KnowledgeBase,
        MemoryEntry,
        MemoryType,
        RAGSystem,
        get_memory_system,
    )
except ImportError:
    # memory_system may fail if sentence_transformers/torch have issues
    AgentMemory = None  # type: ignore
    ConversationHistory = None  # type: ignore
    KnowledgeBase = None  # type: ignore
    MemoryEntry = None  # type: ignore
    MemoryType = None  # type: ignore
    RAGSystem = None  # type: ignore
    get_memory_system = None  # type: ignore

try:
    from .multimodal import (
        CodeAnalyzer,
        DataVisualizer,
        DocumentProcessor,
        ImageProcessor,
    )
except ImportError:
    CodeAnalyzer = None  # type: ignore
    DataVisualizer = None  # type: ignore
    DocumentProcessor = None  # type: ignore
    ImageProcessor = None  # type: ignore

from .tool_framework import (
    Tool,
    ToolExecutor,
    ToolParameter,
    ToolRegistry,
    create_tool,
    get_tool_registry,
    register_tool,
)

__all__ = [
    # Execution Engine
    "AgentExecutionEngine",
    "AgentWorkspace",
    "ExecutionResult",
    "ExecutionLanguage",
    "ToolType",
    "ToolCall",
    "SecureSandbox",
    "FileOperations",
    "WebOperations",
    "get_execution_engine",
    "execute_code",
    "web_search",
    "browse_url",
    # Tool Framework
    "Tool",
    "ToolParameter",
    "ToolRegistry",
    "ToolExecutor",
    "create_tool",
    "register_tool",
    "get_tool_registry",
    # Memory System
    "AgentMemory",
    "MemoryType",
    "MemoryEntry",
    "ConversationHistory",
    "KnowledgeBase",
    "RAGSystem",
    "get_memory_system",
    # Multi-modal
    "ImageProcessor",
    "DocumentProcessor",
    "CodeAnalyzer",
    "DataVisualizer",
]

__version__ = "1.0.0"
