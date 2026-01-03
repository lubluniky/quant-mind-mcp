# QuantMind MCP - Local Setup Guide

## Installation

1. **Clone and setup**:
   ```bash
   git clone <repo-url>
   cd quant-mind-mcp
   pip install -e .
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

Start the MCP server via STDIO:
```bash
python src/server/mcp_server.py
```

The server will accept requests via standard input/output with no authentication required.

## Configure Claude Desktop

Add this to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "quant-mind": {
      "command": "python",
      "args": ["/path/to/quant-mind-mcp/src/server/mcp_server.py"]
    }
  }
}
```

Replace `/path/to/quant-mind-mcp` with your actual installation path.

## Features

- Local STDIO-based MCP server
- No authentication required
- Simple pip install workflow
- Direct integration with Claude Desktop
