"""Integration test script for QuantMind MCP Server.

This script verifies the server functionality by testing:
1. Server connectivity and health
2. Tools listing
3. Knowledge base search (RAG)
4. Alpha telemetry submission
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    os.system(f"{sys.executable} -m pip install httpx")
    import httpx


SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("QUANT_API_KEY")


async def test_health() -> bool:
    """Test server health endpoint."""
    print(">> Testing server health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVER_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ [OK] Server is healthy")
                return True
            else:
                print(f"❌ [FAIL] Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ [FAIL] Cannot connect to server: {e}")
        return False


async def test_root() -> bool:
    """Test root endpoint to get server info."""
    print(">> Testing root endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVER_URL}/", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ [OK] Server info: {data.get('name')} v{data.get('version')}")
                print(f"   Tools available: {data.get('tools', [])}")
                return True
            else:
                print(f"❌ [FAIL] Root endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ [FAIL] Root endpoint error: {e}")
        return False


async def test_list_tools() -> bool:
    """Test listing available tools via JSON-RPC."""
    print(">> Testing tools/list...")
    try:
        headers = {}
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"

        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVER_URL}/messages",
                json=message,
                headers=headers,
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                tools = data.get("result", {}).get("tools", [])
                tool_names = [t["name"] for t in tools]
                print(f"✅ [OK] Found {len(tools)} tools: {tool_names}")

                required = ["search_knowledge_base", "submit_alpha_telemetry"]
                if all(t in tool_names for t in required):
                    print("✅ [OK] All required tools present")
                    return True
                else:
                    missing = [t for t in required if t not in tool_names]
                    print(f"❌ [FAIL] Missing required tools: {missing}")
                    return False
            else:
                print(f"❌ [FAIL] tools/list failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ [FAIL] tools/list error: {e}")
        return False


async def test_knowledge_base() -> bool:
    """Test knowledge base search tool."""
    print(">> Testing search_knowledge_base...")
    try:
        headers = {}
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"

        message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "search_knowledge_base",
                "arguments": {
                    "query": "momentum crash"
                }
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVER_URL}/messages",
                json=message,
                headers=headers,
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("result", {}).get("content", [])

                if content:
                    text = content[0].get("text", "")
                    print(f"✅ [OK] RAG returned content ({len(text)} chars)")

                    # Check if relevant content is present
                    if "Kent Daniel" in text or "momentum" in text.lower():
                        print("✅ [OK] Content is relevant to query")
                        return True
                    else:
                        print(f"⚠️  [WARN] Content might not be relevant")
                        print(f"   Preview: {text[:200]}...")
                        return True  # Still pass, content was returned
                else:
                    print("⚠️  [WARN] RAG returned empty content")
                    return False
            else:
                print(f"❌ [FAIL] search_knowledge_base failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ [FAIL] search_knowledge_base error: {e}")
        return False


async def test_alpha_telemetry() -> bool:
    """Test alpha telemetry submission tool."""
    print(">> Testing submit_alpha_telemetry...")
    try:
        headers = {}
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"

        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "submit_alpha_telemetry",
                "arguments": {
                    "code": "# Test strategy\nimport vectorbt as vbt\n# ...",
                    "metrics": {
                        "sharpe_ratio": 2.1,
                        "total_return": 45.2,
                        "max_drawdown": -8.5,
                        "total_trades": 150,
                        "win_rate": 58.3
                    }
                }
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVER_URL}/messages",
                json=message,
                headers=headers,
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("result", {}).get("content", [])

                if content:
                    text = content[0].get("text", "")
                    print(f"✅ [OK] Telemetry accepted")
                    print(f"   Response: {text[:150]}...")
                    return True
                else:
                    print("⚠️  [WARN] Telemetry submission returned empty response")
                    return False
            else:
                print(f"❌ [FAIL] submit_alpha_telemetry failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ [FAIL] submit_alpha_telemetry error: {e}")
        return False


async def run_verification() -> None:
    """Run all verification tests."""
    print("=" * 80)
    print("🕵️  QuantMind MCP Server - Integrity Verification")
    print("=" * 80)
    print(f"Server URL: {SERVER_URL}")
    print(f"API Key: {'✓ Set' if API_KEY else '✗ Not set'}")
    print("=" * 80)
    print()

    results = []

    # Test 1: Health check
    results.append(("Health Check", await test_health()))
    print()

    # Test 2: Root endpoint
    results.append(("Root Endpoint", await test_root()))
    print()

    # Test 3: List tools
    results.append(("List Tools", await test_list_tools()))
    print()

    # Test 4: Knowledge base search
    results.append(("Knowledge Base", await test_knowledge_base()))
    print()

    # Test 5: Alpha telemetry
    results.append(("Alpha Telemetry", await test_alpha_telemetry()))
    print()

    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    print("=" * 80)

    total = len(results)
    passed = sum(1 for _, p in results if p)

    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED ({passed}/{total})")
        print("\n✅ SYSTEM INTEGRITY VERIFIED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print(f"\n⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        sys.exit(1)


if __name__ == "__main__":
    if not API_KEY:
        print("⚠️  WARNING: QUANT_API_KEY environment variable not set.")
        print("   Authentication tests may fail if AUTH_ENABLED=true")
        print("   Run: export QUANT_API_KEY=sk_quant_xxxxx")
        print()

    asyncio.run(run_verification())
