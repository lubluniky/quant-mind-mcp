"""Tools registry for QuantMind MCP Server."""

from typing import Any, Callable, Dict, List

from mcp.types import Tool

from .alpha_vault import submit_alpha_telemetry, submit_alpha_telemetry_tool
from .knowledge_base import search_knowledge_base, search_knowledge_base_tool

# Registry of all available tools
TOOL_HANDLERS: Dict[str, Callable[..., Any]] = {
    "search_knowledge_base": search_knowledge_base,
    "submit_alpha_telemetry": submit_alpha_telemetry,
}

# Tool definitions for MCP protocol
TOOL_DEFINITIONS: List[Tool] = [
    search_knowledge_base_tool,
    submit_alpha_telemetry_tool,
]

__all__ = [
    "TOOL_HANDLERS",
    "TOOL_DEFINITIONS",
    "search_knowledge_base",
    "submit_alpha_telemetry",
]
