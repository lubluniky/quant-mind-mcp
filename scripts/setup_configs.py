import json
import os
import sys
from pathlib import Path


def setup():
    """
    Automatically generates configuration files for various MCP clients
    with absolute paths based on the current installation directory.
    """
    # Determine the base path of the project (one level up from scripts/)
    base_path = Path(__file__).parent.parent.absolute()

    # Determine python executable path
    if sys.platform == "win32":
        venv_python = base_path / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = base_path / "venv" / "bin" / "python3"

    main_py = base_path / "main.py"

    print(f"🔍 Detected project root: {base_path}")
    print(f"🔍 Using python from: {venv_python}")

    # 1. Claude Desktop Configuration
    claude_config = {
        "mcpServers": {
            "quantmind": {
                "command": str(venv_python),
                "args": [str(main_py)],
                "env": {"ENVIRONMENT": "production", "LOG_LEVEL": "INFO"},
            }
        }
    }

    # 2. Zed Editor Configuration
    zed_config = {
        "context_providers": {
            "mcp": {"quantmind": {"command": str(venv_python), "args": [str(main_py)]}}
        }
    }

    # 3. VS Code (Mcp Client extension) Configuration
    vscode_config = {
        "mcp.servers": {"quantmind": {"command": str(venv_python), "args": [str(main_py)]}}
    }

    # Save generated configs to the root directory
    configs = [
        ("generated_claude_config.json", claude_config),
        ("generated_zed_config.json", zed_config),
        ("generated_vscode_config.json", vscode_config),
    ]

    for filename, data in configs:
        file_path = base_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Generated {filename}")

    print("\n" + "=" * 50)
    print("SETUP INSTRUCTIONS")
    print("=" * 50)

    print(f"\n1. FOR CLAUDE DESKTOP:")
    print(f"   Copy the content of 'generated_claude_config.json' to:")
    if sys.platform == "darwin":
        print(f"   ~/Library/Application Support/Claude/claude_desktop_config.json")
    elif sys.platform == "win32":
        print(f"   %APPDATA%\\Claude\\claude_desktop_config.json")

    print(f"\n2. FOR ZED EDITOR:")
    print(f"   Add the content of 'generated_zed_config.json' to your settings.json")

    print(f"\n3. FOR CLAUDE CODE / TERMINAL:")
    print(f"   Run the following command:")
    print(f"   mcp install {main_py} --python {venv_python}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    setup()
