#!/bin/bash
# Start QuantMind MCP Server

set -e

echo "Starting QuantMind MCP Server..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import mcp" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -e .
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

# Start server
echo ""
echo "Starting server on http://0.0.0.0:8000"
echo "Press Ctrl+C to stop"
echo ""

python main.py
