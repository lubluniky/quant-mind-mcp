#!/bin/bash
# Helper script to activate venv
# Usage: source activate.sh

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated (Python $(python --version))"
    echo ""
    echo "Available commands:"
    echo "  python test_server.py    - Test server setup"
    echo "  python main.py           - Run MCP server (STDIO mode)"
    echo "  deactivate               - Exit virtual environment"
else
    echo "❌ Virtual environment not found. Run: bash scripts/install.sh"
fi
