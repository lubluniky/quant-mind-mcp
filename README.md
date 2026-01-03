# QuantMind MCP

**Quantitative Analysis and Financial Modeling AI Platform**

A Model Context Protocol (MCP) server providing advanced quantitative analysis, financial modeling, and research capabilities to AI applications.

## Project Architecture

### Core Modules

- **`src/server/`** - MCP server implementation handling protocol communications and request routing
- **`src/auth/`** - API key validation and authentication mechanisms
- **`src/tools/`** - Tool implementations for analysis, modeling, and research operations
- **`src/db/`** - Alpha Vault database manager for persistent data storage

### Asset Management

- **`assets/research_papers/`** - Repository for research papers and financial documents (PDFs)
- **`assets/prompts/`** - Prompt templates and configurations (managed by @PromptEngineer)

### Administration

- **`scripts/`** - Administrative and utility scripts

## Directory Structure

```
quant-mind-mcp/
├── assets/
│   ├── research_papers/     (PDF repository)
│   └── prompts/             (Prompt templates)
├── src/
│   ├── server/              (MCP server logic)
│   ├── auth/                (API key validation)
│   ├── tools/               (Tool implementations)
│   └── db/                  (Alpha Vault database)
├── scripts/                 (Admin scripts)
├── .gitignore
└── README.md
```

## Getting Started

### Installation

```bash
# Clone repository
git clone <repository-url>
cd quant-mind-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate configuration for your IDE (Claude Desktop, Zed, VS Code)
python3 scripts/setup_configs.py
```

### Configuration & Setup

1. **Automatic Setup**:
   The `scripts/setup_configs.py` script detects your project's absolute path and generates ready-to-use JSON configurations for:
   - **Claude Desktop**: Copy content from `generated_claude_config.json`.
   - **Zed Editor**: Add content from `generated_zed_config.json` to your settings.
   - **VS Code**: Use `generated_vscode_config.json`.

2. **Manual Configuration**:
   - Set up environment variables in a `.env` file if needed.
   - Research papers should be placed in `assets/research_papers/` (Markdown format supported).

## Development

### Project Team

- **@PromptEngineer** - Prompt design and optimization
- **@Architect** - Project structure and architecture
- **@Developer** - Implementation and integration

## License

Proprietary - QuantMind MCP
