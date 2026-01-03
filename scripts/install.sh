#!/bin/bash
# QuantMind MCP Server - Local Install Script

set -e

echo "Setting up QuantMind MCP Server..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs assets/research_papers assets/prompts

# Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example - please configure as needed"
fi

echo "Setup complete! Run: source venv/bin/activate && python main.py"
