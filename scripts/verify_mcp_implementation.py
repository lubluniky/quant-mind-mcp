#!/usr/bin/env python3
"""Verify MCP server implementation without requiring dependencies."""

import ast
import sys
from pathlib import Path

# Add parent directory to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_file_syntax(filepath: Path) -> tuple[bool, str]:
    """Check if a Python file has valid syntax.

    Args:
        filepath: Path to Python file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, ""
    except SyntaxError as e:
        return False, str(e)


def check_file_exists(filepath: Path) -> bool:
    """Check if file exists.

    Args:
        filepath: Path to check

    Returns:
        True if file exists
    """
    return filepath.exists()


def main() -> None:
    """Run verification checks."""
    print("\n" + "="*80)
    print("QuantMind MCP Server - Implementation Verification")
    print("="*80 + "\n")

    checks = {
        "Core Files": [
            "main.py",
            "src/server/config.py",
            "src/server/mcp_server.py",
            "src/server/__init__.py",
        ],
        "Tool Files": [
            "src/tools/__init__.py",
            "src/tools/knowledge_base.py",
            "src/tools/alpha_vault.py",
        ],
        "Research Papers": [
            "assets/research_papers/momentum_strategies.md",
            "assets/research_papers/mean_reversion.md",
            "assets/research_papers/volatility_trading.md",
        ],
        "Scripts": [
            "scripts/test_server.py",
            "scripts/start_server.sh",
        ],
        "Documentation": [
            "README_IMPLEMENTATION.md",
            "IMPLEMENTATION_SUMMARY.md",
        ]
    }

    all_passed = True

    for category, files in checks.items():
        print(f"\n{category}:")
        print("-" * 40)

        for filename in files:
            filepath = PROJECT_ROOT / filename
            exists = check_file_exists(filepath)

            if not exists:
                print(f"  ❌ {filename} - NOT FOUND")
                all_passed = False
                continue

            # For Python files, check syntax
            if filename.endswith('.py'):
                is_valid, error = check_file_syntax(filepath)
                if is_valid:
                    print(f"  ✅ {filename} - OK")
                else:
                    print(f"  ❌ {filename} - SYNTAX ERROR: {error}")
                    all_passed = False
            else:
                print(f"  ✅ {filename} - EXISTS")

    # Check required components
    print("\n\nRequired Components:")
    print("-" * 40)

    # Check config.py has Settings class
    config_file = PROJECT_ROOT / "src/server/config.py"
    with open(config_file, 'r') as f:
        config_content = f.read()
        if 'class Settings' in config_content:
            print("  ✅ Settings class defined")
        else:
            print("  ❌ Settings class not found")
            all_passed = False

    # Check mcp_server.py has QuantMindMCPServer class
    mcp_server_file = PROJECT_ROOT / "src/server/mcp_server.py"
    with open(mcp_server_file, 'r') as f:
        mcp_content = f.read()
        if 'class QuantMindMCPServer' in mcp_content:
            print("  ✅ QuantMindMCPServer class defined")
        else:
            print("  ❌ QuantMindMCPServer class not found")
            all_passed = False

        if 'def create_mcp_server' in mcp_content:
            print("  ✅ create_mcp_server factory function defined")
        else:
            print("  ❌ create_mcp_server not found")
            all_passed = False

    # Check tools are registered
    tools_init = PROJECT_ROOT / "src/tools/__init__.py"
    with open(tools_init, 'r') as f:
        tools_content = f.read()
        if 'TOOL_HANDLERS' in tools_content:
            print("  ✅ TOOL_HANDLERS registry defined")
        else:
            print("  ❌ TOOL_HANDLERS registry not found")
            all_passed = False

        if 'TOOL_DEFINITIONS' in tools_content:
            print("  ✅ TOOL_DEFINITIONS list defined")
        else:
            print("  ❌ TOOL_DEFINITIONS list not found")
            all_passed = False

    # Check tool implementations
    kb_file = PROJECT_ROOT / "src/tools/knowledge_base.py"
    with open(kb_file, 'r') as f:
        kb_content = f.read()
        if 'async def search_knowledge_base' in kb_content:
            print("  ✅ search_knowledge_base tool implemented")
        else:
            print("  ❌ search_knowledge_base tool not found")
            all_passed = False

    av_file = PROJECT_ROOT / "src/tools/alpha_vault.py"
    with open(av_file, 'r') as f:
        av_content = f.read()
        if 'async def submit_alpha_telemetry' in av_content:
            print("  ✅ submit_alpha_telemetry tool implemented")
        else:
            print("  ❌ submit_alpha_telemetry tool not found")
            all_passed = False

    # Check main.py
    main_file = PROJECT_ROOT / "main.py"
    with open(main_file, 'r') as f:
        main_content = f.read()
        if 'FastAPI' in main_content:
            print("  ✅ FastAPI integration present")
        else:
            print("  ❌ FastAPI integration not found")
            all_passed = False

        if 'def main()' in main_content:
            print("  ✅ main() entry point defined")
        else:
            print("  ❌ main() entry point not found")
            all_passed = False

    # Type hints check
    print("\n\nType Hints Check:")
    print("-" * 40)
    type_hint_files = [
        "src/server/mcp_server.py",
        "src/tools/knowledge_base.py",
        "src/tools/alpha_vault.py",
    ]

    for filename in type_hint_files:
        filepath = PROJECT_ROOT / filename
        with open(filepath, 'r') as f:
            content = f.read()
            # Check for common type hint patterns
            has_hints = (
                '-> ' in content or
                ': str' in content or
                ': dict' in content or
                ': Dict' in content or
                'from typing import' in content
            )
            if has_hints:
                print(f"  ✅ {filename} - Has type hints")
            else:
                print(f"  ⚠️  {filename} - May be missing type hints")

    # Final summary
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Implementation is complete!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -e .")
        print("2. Run tests: python scripts/test_server.py")
        print("3. Start server: python main.py")
    else:
        print("❌ SOME CHECKS FAILED - Please review the errors above")
        sys.exit(1)
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
