"""Main entry point for QuantMind MCP Server with STDIO transport."""

import asyncio
import logging

from src.server.config import settings
from src.server.mcp_server import create_mcp_server

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the MCP server.

    Runs the server using STDIO transport for Claude Desktop integration.
    This is the standard MCP transport for local tool providers.
    """
    logger.info("Starting QuantMind MCP Server")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Research papers path: {settings.research_papers_path}")
    logger.info(f"Database URL: {settings.database_url}")

    # Create and run MCP server with STDIO transport
    server = create_mcp_server()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
