# QuantMind MCP - Quick Start Guide

## TL;DR

```bash
# 1. Install dependencies (requires Python 3.10+)
pip install -r requirements.txt

# 2. Verify setup
python3 verify_stdio_setup.py

# 3. Test run (Ctrl+C to stop)
python3 main.py

# 4. Configure Claude Desktop
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
# Add the config from claude_desktop_config.json (update paths!)

# 5. Restart Claude Desktop
# Server will start automatically when needed
```

## What Changed?

This is now a **LOCAL STDIO MCP server** for Claude Desktop, not a remote FastAPI server.

- **Before:** HTTP server with authentication
- **After:** Local STDIO process (no network, no auth)

## Key Files

- `main.py` - Simple STDIO server runner
- `src/server/mcp_server.py` - MCP protocol implementation
- `src/tools/` - Tool implementations (knowledge base, alpha vault)
- `.env` - Configuration (no HTTP/auth settings)
- `claude_desktop_config.json` - Example Claude Desktop config

## Available Tools

1. **search_knowledge_base** - Search quantitative finance research papers
2. **submit_alpha_telemetry** - Submit successful strategy metrics

## Requirements

- Python 3.10+ (MCP SDK limitation)
- Dependencies: mcp, pydantic, pydantic-settings, sqlalchemy, aiosqlite

## Configuration

Edit `.env`:
```bash
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./data/quantmind.db
ALPHA_VAULT_MIN_SHARPE=1.5
ALPHA_VAULT_MIN_TRADES=100
RESEARCH_PAPERS_PATH=./assets/research_papers
PROMPTS_PATH=./assets/prompts
LOG_LEVEL=INFO
```

## Claude Desktop Setup

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "quantmind": {
      "command": "python3",
      "args": ["/absolute/path/to/quant-mind-mcp/main.py"]
    }
  }
}
```

**IMPORTANT:** Use absolute path, not relative!

## Troubleshooting

**Import errors?**
```bash
pip install -r requirements.txt
```

**Python version error?**
```bash
python3 --version  # Must be 3.10+
```

**Server not working in Claude Desktop?**
1. Check absolute path in config
2. Restart Claude Desktop
3. Check Claude Desktop logs

## Documentation

- `STDIO_SETUP.md` - Complete setup guide
- `REFACTORING_SUMMARY.md` - What changed and why
- `CHANGES.md` - File-by-file changes
- `verify_stdio_setup.py` - Automated verification

## Need Help?

Run verification:
```bash
python3 verify_stdio_setup.py
```

All checks should pass. If not, see error messages for details.
