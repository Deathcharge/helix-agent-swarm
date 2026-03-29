"""
Helix Agent Tool Framework
==========================
A flexible framework for defining, registering, and executing tools
that agents can use. Similar to Claude's tool-use or OpenAI's function calling.

Features:
- Declarative tool definitions with JSON Schema
- Automatic parameter validation
- Tool composition and chaining
- Async execution support
- Tool versioning and deprecation
- Usage tracking and analytics
"""

import asyncio
import functools
import inspect
import json
import logging
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, get_type_hints

logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """Supported parameter types"""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Definition of a tool parameter"""

    name: str
    type: ParameterType | None
    description: str
    required: bool = True
    default: Any = None
    enum: list[Any] | None = None
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    items_type: ParameterType | None = None  # For arrays
    properties: dict[str, "ToolParameter"] | None = None  # For objects

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema format"""
        if self.type is not None:
            schema = {"type": self.type.value, "description": self.description}
        else:
            schema = {"description": self.description}  # No type constraint

        if self.enum:
            schema["enum"] = self.enum
        if self.min_value is not None:
            schema["minimum"] = self.min_value
        if self.max_value is not None:
            schema["maximum"] = self.max_value
        if self.min_length is not None:
            schema["minLength"] = self.min_length
        if self.max_length is not None:
            schema["maxLength"] = self.max_length
        if self.pattern:
            schema["pattern"] = self.pattern
        if self.items_type and self.type == ParameterType.ARRAY:
            schema["items"] = {"type": self.items_type.value}
        if self.properties and self.type == ParameterType.OBJECT:
            schema["properties"] = {name: param.to_json_schema() for name, param in self.properties.items()}
        if self.default is not None:
            schema["default"] = self.default

        return schema

    def validate(self, value: Any) -> tuple[bool, str | None]:
        """Validate a value against this parameter definition"""
        if value is None:
            if self.required and self.default is None:
                return False, f"Parameter '{self.name}' is required"
            return True, None

        # Type validation
        if self.type is not None:
            type_checks = {
                ParameterType.STRING: lambda v: isinstance(v, str),
                ParameterType.INTEGER: lambda v: isinstance(v, int) and not isinstance(v, bool),
                ParameterType.NUMBER: lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
                ParameterType.BOOLEAN: lambda v: isinstance(v, bool),
                ParameterType.ARRAY: lambda v: isinstance(v, list),
                ParameterType.OBJECT: lambda v: isinstance(v, dict),
            }

            if not type_checks[self.type](value):
                return (
                    False,
                    f"Parameter '{self.name}' must be of type {self.type.value}",
                )

        # Enum validation
        if self.enum and value not in self.enum:
            return False, f"Parameter '{self.name}' must be one of {self.enum}"

        # Range validation for numbers
        if self.type in (ParameterType.INTEGER, ParameterType.NUMBER):
            if self.min_value is not None and value < self.min_value:
                return False, f"Parameter '{self.name}' must be >= {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"Parameter '{self.name}' must be <= {self.max_value}"

        # Length validation for strings and arrays
        if self.type in (ParameterType.STRING, ParameterType.ARRAY):
            if self.min_length is not None and len(value) < self.min_length:
                return (
                    False,
                    f"Parameter '{self.name}' must have length >= {self.min_length}",
                )
            if self.max_length is not None and len(value) > self.max_length:
                return (
                    False,
                    f"Parameter '{self.name}' must have length <= {self.max_length}",
                )

        # Pattern validation for strings
        if self.type == ParameterType.STRING and self.pattern:
            import re

            if not re.match(self.pattern, value):
                return (
                    False,
                    f"Parameter '{self.name}' must match pattern {self.pattern}",
                )

        return True, None


@dataclass
class ToolResult:
    """Result of a tool execution"""

    success: bool
    output: Any
    error: str | None = None
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }


@dataclass
class Tool:
    """Definition of a tool that agents can use"""

    name: str
    description: str
    parameters: list[ToolParameter]
    handler: Callable
    version: str = "1.0.0"
    deprecated: bool = False
    deprecation_message: str | None = None
    category: str = "general"
    tags: list[str] = field(default_factory=list)
    examples: list[dict[str, Any]] = field(default_factory=list)
    requires_workspace: bool = False
    timeout_seconds: int = 30
    result_as_answer: bool = False  # If True, tool output is the final answer (skip LLM reformulation)
    max_usage_count: int | None = None  # Max times this tool can be called per agentic session

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema format for LLM consumption"""
        required = [p.name for p in self.parameters if p.required]
        properties = {p.name: p.to_json_schema() for p in self.parameters}

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function calling format"""
        return {"type": "function", "function": self.to_json_schema()}

    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert to Anthropic tool format"""
        schema = self.to_json_schema()
        return {
            "name": schema["name"],
            "description": schema["description"],
            "input_schema": schema["parameters"],
        }

    def validate_parameters(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters against tool definition"""
        errors = []

        for param in self.parameters:
            value = params.get(param.name, param.default)
            is_valid, error = param.validate(value)
            if not is_valid:
                errors.append(error)

        # Check for unknown parameters
        known_params = {p.name for p in self.parameters}
        unknown = set(params.keys()) - known_params
        if unknown:
            errors.append(f"Unknown parameters: {unknown}")

        return len(errors) == 0, errors

    async def execute(self, params: dict[str, Any], context: dict | None = None) -> ToolResult:
        """Execute the tool with given parameters"""
        start_time = datetime.now(UTC)

        # Validate parameters
        is_valid, errors = self.validate_parameters(params)
        if not is_valid:
            return ToolResult(
                success=False,
                output=None,
                error=f"Parameter validation failed: {'; '.join(errors)}",
            )

        # Apply defaults
        for param in self.parameters:
            if param.name not in params and param.default is not None:
                params[param.name] = param.default

        try:
            if asyncio.iscoroutinefunction(self.handler):
                if context:
                    result = await asyncio.wait_for(self.handler(params, context), timeout=self.timeout_seconds)
                else:
                    result = await asyncio.wait_for(self.handler(params), timeout=self.timeout_seconds)
            else:
                if context:
                    result = self.handler(params, context)
                else:
                    result = self.handler(params)

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            # Handle different return types
            if isinstance(result, ToolResult):
                result.execution_time_ms = execution_time
                return result
            else:
                return ToolResult(success=True, output=result, execution_time_ms=execution_time)

        except TimeoutError:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool execution timed out after {self.timeout_seconds} seconds",
            )
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.warning("Tool execution validation error: %s", e)
            return ToolResult(success=False, output=None, error=f"{type(e).__name__}: {e!s}")
        except Exception as e:
            logger.exception("Unexpected error executing tool")
            return ToolResult(success=False, output=None, error=f"{type(e).__name__}: {e!s}")


class ToolRegistry:
    """Registry for managing available tools"""

    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self.categories: dict[str, list[str]] = {}
        self.usage_stats: dict[str, dict[str, Any]] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool"""
        self.tools[tool.name] = tool

        # Update category index
        if tool.category not in self.categories:
            self.categories[tool.category] = []
        if tool.name not in self.categories[tool.category]:
            self.categories[tool.category].append(tool.name)

        # Initialize usage stats
        self.usage_stats[tool.name] = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_execution_time_ms": 0,
            "last_used": None,
        }

    def unregister(self, name: str) -> bool:
        """Unregister a tool"""
        if name in self.tools:
            tool = self.tools.pop(name)
            if tool.category in self.categories:
                self.categories[tool.category].remove(name)
            return True
        return False

    def get(self, name: str) -> Tool | None:
        """Get a tool by name"""
        return self.tools.get(name)

    def list_tools(self, category: str | None = None) -> list[Tool]:
        """List all tools, optionally filtered by category"""
        if category:
            tool_names = self.categories.get(category, [])
            return [self.tools[name] for name in tool_names]
        return list(self.tools.values())

    def get_schemas(self, format: str = "json") -> list[dict[str, Any]]:
        """Get schemas for all tools in specified format"""
        schemas = []
        for tool in self.tools.values():
            if not tool.deprecated:
                if format == "openai":
                    schemas.append(tool.to_openai_format())
                elif format == "anthropic":
                    schemas.append(tool.to_anthropic_format())
                else:
                    schemas.append(tool.to_json_schema())
        return schemas

    async def execute(self, tool_name: str, params: dict[str, Any], context: dict | None = None) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(success=False, output=None, error=f"Tool not found: {tool_name}")

        if tool.deprecated:
            # Log deprecation warning but still execute
            logger.warning("Warning: Tool '%s' is deprecated. %s", tool_name, tool.deprecation_message or "")

        result = await tool.execute(params, context)

        # Update usage stats
        stats = self.usage_stats[tool_name]
        stats["total_calls"] += 1
        if result.success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
        stats["total_execution_time_ms"] += result.execution_time_ms
        stats["last_used"] = datetime.now(UTC).isoformat()

        return result

    def get_usage_stats(self, tool_name: str | None = None) -> dict[str, Any]:
        """Get usage statistics"""
        if tool_name:
            return self.usage_stats.get(tool_name, {})
        return self.usage_stats


class ToolExecutor:
    """
    High-level executor for running tools with context management,
    chaining, and error handling.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_history: list[dict[str, Any]] = []
        self.max_history = 1000

    async def execute(self, tool_name: str, params: dict[str, Any], context: dict | None = None) -> ToolResult:
        """Execute a single tool"""
        execution_id = str(uuid.uuid4())
        start_time = datetime.now(UTC)

        result = await self.registry.execute(tool_name, params, context)

        # Record execution
        self._record_execution(
            {
                "execution_id": execution_id,
                "tool_name": tool_name,
                "params": params,
                "result": result.to_dict(),
                "timestamp": start_time.isoformat(),
            }
        )

        return result

    async def execute_chain(
        self,
        chain: list[dict[str, Any]],
        context: dict | None = None,
        stop_on_error: bool = True,
    ) -> list[ToolResult]:
        """
        Execute a chain of tools in sequence.
        Each tool can reference outputs from previous tools using {{step_N.output}}
        """
        results = []
        step_outputs = {}

        for i, step in enumerate(chain):
            tool_name = step.get("tool")
            params = step.get("params", {})

            # Resolve references to previous outputs
            resolved_params = self._resolve_references(params, step_outputs)

            result = await self.execute(tool_name, resolved_params, context)
            results.append(result)
            step_outputs[f"step_{i}"] = result.output

            if not result.success and stop_on_error:
                break

        return results

    async def execute_parallel(self, tools: list[dict[str, Any]], context: dict | None = None) -> list[ToolResult]:
        """Execute multiple tools in parallel"""
        tasks = [self.execute(t.get("tool"), t.get("params", {}), context) for t in tools]
        return await asyncio.gather(*tasks)

    def _resolve_references(self, params: dict[str, Any], step_outputs: dict[str, Any]) -> dict[str, Any]:
        """Resolve references like {{step_0.output}} in parameters"""

        resolved = {}
        for key, value in params.items():
            if isinstance(value, str):
                # Find all references
                matches = re.findall(r"\{\{(\w+)\.(\w+)\}\}", value)
                for step_name, attr in matches:
                    if step_name in step_outputs:
                        output = step_outputs[step_name]
                        if isinstance(output, dict) and attr in output:
                            replacement = output[attr]
                        elif attr == "output":
                            replacement = output
                        else:
                            replacement = ""
                        value = value.replace(f"{{{{{step_name}.{attr}}}}}", str(replacement))
                resolved[key] = value
            elif isinstance(value, dict):
                resolved[key] = self._resolve_references(value, step_outputs)
            else:
                resolved[key] = value

        return resolved

    def _record_execution(self, record: dict[str, Any]) -> None:
        """Record an execution in history"""
        self.execution_history.append(record)
        if len(self.execution_history) > self.max_history:
            self.execution_history = self.execution_history[-self.max_history :]

    def get_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:]


# Decorator for creating tools from functions
def create_tool(
    name: str | None = None,
    description: str | None = None,
    category: str = "general",
    tags: list[str] | None = None,
    timeout: int = 30,
):
    """
    Decorator to create a tool from a function.
    Automatically extracts parameters from function signature and type hints.

    Usage:
        @create_tool(name="my_tool", description="Does something useful")
        async def my_tool(text: str, count: int = 5) -> str:
            return text * count
    """

    def decorator(func: Callable) -> Tool:
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Tool: {tool_name}"

        # Extract parameters from function signature
        sig = inspect.signature(func)
        hints = get_type_hints(func) if hasattr(func, "__annotations__") else {}

        parameters = []
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls", "context"):
                continue

            # Determine type
            param_type = hints.get(param_name, str)
            if param_type == str:
                ptype = ParameterType.STRING
            elif param_type == int:
                ptype = ParameterType.INTEGER
            elif param_type == float:
                ptype = ParameterType.NUMBER
            elif param_type == bool:
                ptype = ParameterType.BOOLEAN
            elif param_type == list or (hasattr(param_type, "__origin__") and param_type.__origin__ == list):
                ptype = ParameterType.ARRAY
            elif param_type == dict or (hasattr(param_type, "__origin__") and param_type.__origin__ == dict):
                ptype = ParameterType.OBJECT
            else:
                ptype = ParameterType.STRING

            # Determine if required
            required = param.default == inspect.Parameter.empty
            default = None if required else param.default

            parameters.append(
                ToolParameter(
                    name=param_name,
                    type=ptype,
                    description=f"Parameter: {param_name}",
                    required=required,
                    default=default,
                )
            )

        # Create wrapper that unpacks params dict
        @functools.wraps(func)
        async def wrapper(params: dict[str, Any], context: dict | None = None):
            if asyncio.iscoroutinefunction(func):
                return await func(**params)
            return func(**params)

        tool = Tool(
            name=tool_name,
            description=tool_description,
            parameters=parameters,
            handler=wrapper,
            category=category,
            tags=tags or [],
            timeout_seconds=timeout,
        )

        return tool

    return decorator


# Global registry instance
_tool_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
        _register_builtin_tools(_tool_registry)
    return _tool_registry


def register_tool(tool: Tool) -> None:
    """Register a tool in the global registry"""
    get_tool_registry().register(tool)


def _register_builtin_tools(registry: ToolRegistry) -> None:
    """Register built-in tools"""
    from .execution_engine import get_execution_engine

    get_execution_engine()

    # Calculator tool
    @create_tool(
        name="calculator",
        description="Perform mathematical calculations. Supports basic arithmetic, trigonometry, and common math functions.",
        category="math",
    )
    def calculator(expression: str) -> str:
        import math

        # Safe eval for math expressions
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed_names.update(
            {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "int": int,
                "float": float,
            }
        )
        try:
            from utils.safe_eval import SafeEvaluator

            evaluator = SafeEvaluator(allowed_names=allowed_names)
            result = evaluator.eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    registry.register(calculator)

    # Current time tool
    @create_tool(
        name="current_time",
        description="Get the current date and time",
        category="utility",
    )
    def current_time(timezone: str = "UTC") -> str:
        import pytz

        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return now.strftime("%Y-%m-%d %H:%M:%S %Z")
        except Exception as e:
            logging.getLogger(__name__).debug("Timezone lookup failed for %s: %s", timezone, e)
            return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    registry.register(current_time)

    # JSON formatter tool
    @create_tool(
        name="format_json",
        description="Format and validate JSON data",
        category="utility",
    )
    def format_json(data: str, indent: int = 2) -> str:
        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=indent, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {e}"

    registry.register(format_json)

    # Text analysis tool
    @create_tool(
        name="analyze_text",
        description="Analyze text for word count, character count, and basic statistics",
        category="text",
    )
    def analyze_text(text: str) -> str:
        words = text.split()
        sentences = text.count(".") + text.count("!") + text.count("?")
        paragraphs = text.count("\n\n") + 1

        result = {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": sentences,
            "paragraph_count": paragraphs,
            "average_word_length": (sum(len(w) for w in words) / len(words) if words else 0),
        }
        return json.dumps(result, indent=2)

    registry.register(analyze_text)

    # URL encoder/decoder
    @create_tool(
        name="url_encode",
        description="Encode or decode URL strings",
        category="utility",
    )
    def url_encode(text: str, decode: bool = False) -> str:
        from urllib.parse import quote, unquote

        if decode:
            return unquote(text)
        return quote(text)

    registry.register(url_encode)

    # Base64 encoder/decoder
    @create_tool(
        name="base64_encode",
        description="Encode or decode Base64 strings",
        category="utility",
    )
    def base64_encode(text: str, decode: bool = False) -> str:
        import base64

        if decode:
            return base64.b64decode(text.encode()).decode()
        return base64.b64encode(text.encode()).decode()

    registry.register(base64_encode)

    # Hash generator
    @create_tool(
        name="generate_hash",
        description="Generate hash of text using various algorithms",
        category="security",
    )
    def generate_hash(text: str, algorithm: str = "sha256") -> str:
        import hashlib

        algorithms = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }
        if algorithm not in algorithms:
            return f"Unknown algorithm. Supported: {list(algorithms.keys())}"
        return algorithms[algorithm](text.encode()).hexdigest()

    registry.register(generate_hash)

    # UUID generator
    @create_tool(name="generate_uuid", description="Generate a UUID", category="utility")
    def generate_uuid(version: int = 4) -> str:
        if version == 1:
            return str(uuid.uuid1())
        elif version == 4:
            return str(uuid.uuid4())
        return str(uuid.uuid4())

    registry.register(generate_uuid)

    # Regex tester
    @create_tool(
        name="regex_test",
        description="Test a regular expression against text",
        category="text",
    )
    def regex_test(pattern: str, text: str, find_all: bool = False) -> str:
        try:
            if find_all:
                matches = re.findall(pattern, text)
                return json.dumps({"matches": matches, "count": len(matches)})
            else:
                match = re.search(pattern, text)
                if match:
                    return json.dumps(
                        {
                            "matched": True,
                            "match": match.group(),
                            "start": match.start(),
                            "end": match.end(),
                            "groups": match.groups(),
                        }
                    )
                return json.dumps({"matched": False})
        except re.error as e:
            return f"Invalid regex: {e}"

    registry.register(regex_test)

    # Bridge external tool registries (spiral nodes, integrations, MCP)
    try:
        from services.tool_bridge import register_all_bridges

        bridge_stats = register_all_bridges(registry)
        logger.info("Tool bridge registered: %s", bridge_stats)
    except ImportError:
        logger.debug("Tool bridge module not available")
    except Exception as e:
        logger.warning("Tool bridge registration failed: %s", e)

    # Register Composio meta-tools (if COMPOSIO_API_KEY is set)
    try:
        from services.composio_provider import register_composio_meta_tools

        register_composio_meta_tools(registry)
    except ImportError:
        logger.debug("Composio provider not available")
    except Exception as e:
        logger.warning("Composio meta-tool registration failed: %s", e)

    # Register inter-agent delegation tools (delegate_work, ask_agent)
    try:
        from services.delegation_tools import register_delegation_tools

        register_delegation_tools(registry)
    except ImportError:
        logger.debug("Delegation tools module not available")
    except Exception as e:
        logger.warning("Delegation tool registration failed: %s", e)

    # Register agent memory tools (remember_fact, recall_memories, update_core_memory)
    try:
        from services.memory_tools import register_memory_tools

        register_memory_tools(registry)
    except ImportError:
        logger.debug("Memory tools module not available")
    except Exception as e:
        logger.warning("Memory tool registration failed: %s", e)


def create_tool_from_function(func):
    """Create a Tool instance from a function"""
    sig = inspect.signature(func)
    parameters = []

    for param_name, param in sig.parameters.items():
        # Skip 'self' parameter
        if param_name == "self":
            continue

        # Determine parameter type
        if param.annotation != inspect.Parameter.empty:
            if param.annotation == str:
                ptype = ParameterType.STRING
            elif param.annotation == int:
                ptype = ParameterType.INTEGER
            elif param.annotation == float:
                ptype = ParameterType.NUMBER
            elif param.annotation == bool:
                ptype = ParameterType.BOOLEAN
            elif param.annotation == list:
                ptype = ParameterType.ARRAY
            elif param.annotation == dict:
                ptype = ParameterType.OBJECT
            else:
                ptype = ParameterType.STRING  # Default
        else:
            ptype = None  # No type validation for unannotated parameters

        required = param.default == inspect.Parameter.empty
        default = None if required else param.default

        parameters.append(
            ToolParameter(
                name=param_name,
                type=ptype,
                description=f"Parameter: {param_name}",
                required=required,
                default=default,
            )
        )

    # Create wrapper that unpacks params dict
    @functools.wraps(func)
    async def wrapper(params: dict[str, Any], context: dict | None = None):
        if asyncio.iscoroutinefunction(func):
            return await func(**params)
        return func(**params)

    tool = Tool(
        name=func.__name__,
        description=func.__doc__ or f"Tool: {func.__name__}",
        parameters=parameters,
        handler=wrapper,
        category="general",
        tags=[],
        timeout_seconds=30,
    )

    return tool


class ToolFramework:
    """High-level framework for managing and executing tools"""

    def __init__(self):
        self.registry = ToolRegistry()
        self.executor = ToolExecutor(self.registry)

    def register(self, func):
        """Decorator to register a tool"""
        # Extract function signature and create tool
        tool = create_tool_from_function(func)
        self.registry.register(tool)
        return func

    def list_tools(self):
        """List all registered tools"""
        tools = []
        for name, tool in self.registry.tools.items():
            tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": [
                        {
                            "name": param.name,
                            "type": param.type.value if param.type else "any",
                            "description": param.description,
                            "required": param.required,
                        }
                        for param in tool.parameters
                    ],
                }
            )
        return tools

    async def execute(self, tool_name, **kwargs):
        """Execute a tool with given parameters"""
        try:
            result = await self.executor.execute(tool_name, kwargs)
            if result.success:
                return {"success": True, "data": result.output}
            else:
                return {"success": False, "error": result.error}
        except Exception as e:
            return {"success": False, "error": str(e)}
