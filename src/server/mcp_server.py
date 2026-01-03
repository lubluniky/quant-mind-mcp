"""Main MCP server implementation using mcp Python SDK."""

import logging
from typing import Any, List, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)

from ..tools import TOOL_DEFINITIONS, TOOL_HANDLERS

logger = logging.getLogger(__name__)


class QuantMindMCPServer:
    """QuantMind MCP Server - Stateless tools provider for quantitative finance.

    This server provides:
    - Knowledge base search (RAG over research papers)
    - Alpha vault telemetry submission (receives successful strategies)

    Architecture:
    - Server is STATELESS - no strategy execution
    - Server provides scaffolding and accepts telemetry only
    - All tools require authentication (handled by middleware)
    """

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.server = Server("quantmind-mcp")
        self._register_handlers()
        logger.info("QuantMind MCP Server initialized")

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools.

            Returns:
                List of tool definitions
            """
            logger.debug(f"Listing {len(TOOL_DEFINITIONS)} tools")
            return TOOL_DEFINITIONS

        @self.server.call_tool()
        async def call_tool(
            name: str,
            arguments: dict
        ) -> Sequence[TextContent]:
            """Execute a tool by name.

            Args:
                name: Tool name
                arguments: Tool arguments

            Returns:
                Tool execution results

            Raises:
                ValueError: If tool not found
            """
            logger.info(f"Calling tool: {name} with arguments: {arguments}")

            if name not in TOOL_HANDLERS:
                available_tools = ", ".join(TOOL_HANDLERS.keys())
                error_msg = f"Unknown tool: {name}. Available tools: {available_tools}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            try:
                handler = TOOL_HANDLERS[name]
                result = await handler(**arguments)
                logger.info(f"Tool {name} executed successfully")
                return result
            except TypeError as e:
                error_msg = f"Invalid arguments for tool {name}: {e}"
                logger.error(error_msg)
                raise ValueError(error_msg) from e
            except Exception as e:
                error_msg = f"Tool {name} execution failed: {e}"
                logger.error(error_msg, exc_info=True)
                raise

    async def run_stdio(self) -> None:
        """Run server using stdio transport (for local CLI usage).

        This is the standard MCP transport for local tool providers.
        """
        logger.info("Starting MCP server with stdio transport")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

    def get_server(self) -> Server:
        """Get the underlying MCP server instance.

        Returns:
            MCP Server instance
        """
        return self.server


def create_mcp_server() -> QuantMindMCPServer:
    """Factory function to create MCP server instance.

    Returns:
        Configured QuantMindMCPServer instance
    """
    return QuantMindMCPServer()
