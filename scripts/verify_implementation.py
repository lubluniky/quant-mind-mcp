#!/usr/bin/env python3
"""Verification script to check that all components are properly implemented.

This script verifies the API key authentication system implementation without
requiring bcrypt to be installed. It checks code structure and imports.
"""

import ast
import sys
from pathlib import Path


def check_file_exists(file_path: Path) -> bool:
    """Check if a file exists."""
    exists = file_path.exists()
    status = "✓" if exists else "✗"
    print(f"{status} {file_path.relative_to(Path.cwd())}")
    return exists


def check_class_methods(file_path: Path, class_name: str, expected_methods: list) -> bool:
    """Check if a class has the expected methods."""
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                methods = [
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                missing = set(expected_methods) - set(methods)
                if missing:
                    print(f"  ✗ Missing methods in {class_name}: {missing}")
                    return False
                print(f"  ✓ {class_name} has all required methods")
                return True

        print(f"  ✗ Class {class_name} not found in {file_path}")
        return False
    except Exception as e:
        print(f"  ✗ Error checking {file_path}: {e}")
        return False


def check_imports(file_path: Path, expected_imports: list) -> bool:
    """Check if a file has expected imports."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        missing = []
        for imp in expected_imports:
            if imp not in content:
                missing.append(imp)

        if missing:
            print(f"  ✗ Missing imports: {missing}")
            return False

        print(f"  ✓ All required imports present")
        return True
    except Exception as e:
        print(f"  ✗ Error checking imports: {e}")
        return False


def main() -> None:
    """Run verification checks."""
    print("=" * 80)
    print("QuantMind MCP - API Key Authentication System Verification")
    print("=" * 80)
    print()

    base_path = Path.cwd()
    all_checks_passed = True

    # Check file existence
    print("1. Checking file structure...")
    files_to_check = [
        base_path / "src/auth/manager.py",
        base_path / "src/auth/middleware.py",
        base_path / "src/auth/__init__.py",
        base_path / "scripts/generate_key.py",
    ]

    for file_path in files_to_check:
        if not check_file_exists(file_path):
            all_checks_passed = False

    print()

    # Check APIKeyManager class
    print("2. Checking APIKeyManager implementation...")
    manager_file = base_path / "src/auth/manager.py"
    expected_methods = [
        "__init__",
        "generate_api_key",
        "hash_key",
        "verify_key",
        "load_authorized_keys",
        "save_authorized_key",
        "is_key_authorized",
    ]
    if not check_class_methods(manager_file, "APIKeyManager", expected_methods):
        all_checks_passed = False

    # Check imports in manager.py
    if not check_imports(manager_file, ["import bcrypt", "import json", "import secrets"]):
        all_checks_passed = False

    print()

    # Check APIKeyAuthMiddleware class
    print("3. Checking APIKeyAuthMiddleware implementation...")
    middleware_file = base_path / "src/auth/middleware.py"
    expected_methods = ["__init__", "dispatch", "_extract_api_key"]
    if not check_class_methods(middleware_file, "APIKeyAuthMiddleware", expected_methods):
        all_checks_passed = False

    # Check imports in middleware.py
    if not check_imports(
        middleware_file,
        ["from fastapi import", "from starlette.middleware.base import BaseHTTPMiddleware"],
    ):
        all_checks_passed = False

    print()

    # Check generate_key.py script
    print("4. Checking generate_key.py script...")
    script_file = base_path / "scripts/generate_key.py"
    if not check_imports(script_file, ["import argparse", "from auth.manager import APIKeyManager"]):
        all_checks_passed = False

    # Check for main function
    if not check_class_methods(script_file, "NonExistentClass", []):
        # This is expected to fail, just checking file can be parsed
        pass

    try:
        with open(script_file, "r") as f:
            content = f.read()
            if "def main()" in content and 'if __name__ == "__main__"' in content:
                print("  ✓ Script has main() function and entry point")
            else:
                print("  ✗ Script missing main() or entry point")
                all_checks_passed = False
    except Exception as e:
        print(f"  ✗ Error checking script: {e}")
        all_checks_passed = False

    print()

    # Check __init__.py exports
    print("5. Checking module exports...")
    init_file = base_path / "src/auth/__init__.py"
    try:
        with open(init_file, "r") as f:
            content = f.read()
            required_exports = ["APIKeyManager", "APIKeyAuthMiddleware", "create_api_key_middleware"]
            missing = [exp for exp in required_exports if exp not in content]
            if missing:
                print(f"  ✗ Missing exports: {missing}")
                all_checks_passed = False
            else:
                print("  ✓ All required components exported")
    except Exception as e:
        print(f"  ✗ Error checking exports: {e}")
        all_checks_passed = False

    print()

    # Check type hints
    print("6. Checking for type hints...")
    for file_path in [manager_file, middleware_file]:
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if "->" in content and ": str" in content or ": bool" in content:
                    print(f"  ✓ {file_path.name} has type hints")
                else:
                    print(f"  ✗ {file_path.name} may be missing type hints")
                    all_checks_passed = False
        except Exception as e:
            print(f"  ✗ Error checking type hints in {file_path}: {e}")
            all_checks_passed = False

    print()
    print("=" * 80)

    if all_checks_passed:
        print("✓ All verification checks passed!")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip install -e .")
        print("  2. Generate an API key: python scripts/generate_key.py --name test")
        print("  3. Integrate middleware into your FastAPI app")
    else:
        print("✗ Some verification checks failed.")
        print("Please review the errors above.")
        sys.exit(1)

    print("=" * 80)


if __name__ == "__main__":
    main()
