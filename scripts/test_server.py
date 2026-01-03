#!/usr/bin/env python3
"""Test script for QuantMind MCP Server."""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.knowledge_base import search_knowledge_base
from src.tools.alpha_vault import submit_alpha_telemetry


async def test_knowledge_base() -> None:
    """Test the knowledge base search tool."""
    print("\n" + "="*80)
    print("TEST 1: Knowledge Base Search - 'momentum'")
    print("="*80)

    result = await search_knowledge_base(query="momentum")
    print(result[0].text)


async def test_alpha_vault_success() -> None:
    """Test successful alpha vault submission."""
    print("\n" + "="*80)
    print("TEST 2: Alpha Vault - Successful Submission")
    print("="*80)

    metrics = {
        "name": "Test Momentum Strategy",
        "sharpe_ratio": 2.1,
        "total_trades": 150,
        "returns": 0.25,
        "max_drawdown": -0.12,
        "win_rate": 0.62,
        "timeframe": "1D"
    }

    code = """
# Test Momentum Strategy
def strategy(data):
    # Calculate 12-month momentum
    momentum = data['close'].pct_change(252)

    # Generate signals
    signals = momentum.rank(pct=True)

    # Long top decile, short bottom decile
    positions = (signals > 0.9).astype(int) - (signals < 0.1).astype(int)

    return positions
"""

    result = await submit_alpha_telemetry(metrics=metrics, code=code)
    print(result[0].text)


async def test_alpha_vault_failure() -> None:
    """Test failed alpha vault submission (low Sharpe)."""
    print("\n" + "="*80)
    print("TEST 3: Alpha Vault - Failed Submission (Low Sharpe)")
    print("="*80)

    metrics = {
        "name": "Bad Strategy",
        "sharpe_ratio": 0.8,  # Below minimum
        "total_trades": 150,
        "returns": 0.05,
        "max_drawdown": -0.25,
    }

    code = "# Bad strategy code"

    result = await submit_alpha_telemetry(metrics=metrics, code=code)
    print(result[0].text)


async def test_knowledge_base_no_results() -> None:
    """Test knowledge base search with no results."""
    print("\n" + "="*80)
    print("TEST 4: Knowledge Base Search - No Results")
    print("="*80)

    result = await search_knowledge_base(query="quantum computing trading")
    print(result[0].text)


async def main() -> None:
    """Run all tests."""
    print("\n")
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃                    QuantMind MCP Server Test Suite                        ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    try:
        await test_knowledge_base()
        await test_alpha_vault_success()
        await test_alpha_vault_failure()
        await test_knowledge_base_no_results()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
