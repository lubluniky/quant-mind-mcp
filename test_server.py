#!/usr/bin/env python3
"""Quick test script to verify MCP server is working."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work."""
    print("Testing imports...")

    try:
        from src.server.config import settings
        print(f"  ✅ Config loaded: {settings.environment}")
    except Exception as e:
        print(f"  ❌ Config failed: {e}")
        return False

    try:
        from src.tools import TOOL_HANDLERS, TOOL_DEFINITIONS
        print(f"  ✅ Tools loaded: {list(TOOL_HANDLERS.keys())}")
        print(f"  ✅ Tool definitions: {len(TOOL_DEFINITIONS)}")
    except Exception as e:
        print(f"  ❌ Tools failed: {e}")
        return False

    try:
        from src.server.mcp_server import create_mcp_server
        server = create_mcp_server()
        print(f"  ✅ MCP Server created")
    except Exception as e:
        print(f"  ❌ Server creation failed: {e}")
        return False

    return True


def test_research_papers():
    """Test that research papers are accessible."""
    print("\nTesting research papers...")

    from src.server.config import settings

    papers_path = Path(settings.research_papers_path)
    if not papers_path.exists():
        print(f"  ⚠️  Research papers directory not found: {papers_path}")
        return False

    papers = list(papers_path.glob("*.md"))
    print(f"  ✅ Found {len(papers)} research papers")
    for paper in papers:
        print(f"    - {paper.name}")

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("QuantMind MCP Server - Quick Test")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Research Papers", test_research_papers),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 All tests passed! Server is ready to use.")
        print("\nTo run the server:")
        print("  python main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
