"""Alpha vault tool - Accept and store successful trading strategies."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from mcp.types import TextContent, Tool

from ..server.config import settings

logger = logging.getLogger(__name__)


def _validate_metrics(metrics: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate strategy metrics meet minimum requirements.

    Args:
        metrics: Dictionary containing strategy performance metrics

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["sharpe_ratio", "total_trades", "returns", "max_drawdown"]

    # Check required fields
    for field in required_fields:
        if field not in metrics:
            return False, f"Missing required field: {field}"

    # Validate Sharpe ratio
    try:
        sharpe = float(metrics["sharpe_ratio"])
        if sharpe < settings.alpha_vault_min_sharpe:
            return (
                False,
                f"Sharpe ratio {sharpe:.2f} below minimum {settings.alpha_vault_min_sharpe}",
            )
    except (ValueError, TypeError):
        return False, "Invalid sharpe_ratio value"

    # Validate trade count
    try:
        trades = int(metrics["total_trades"])
        if trades < settings.alpha_vault_min_trades:
            return False, f"Trade count {trades} below minimum {settings.alpha_vault_min_trades}"
    except (ValueError, TypeError):
        return False, "Invalid total_trades value"

    # Validate returns is a number
    try:
        float(metrics["returns"])
    except (ValueError, TypeError):
        return False, "Invalid returns value"

    # Validate max_drawdown is a number
    try:
        float(metrics["max_drawdown"])
    except (ValueError, TypeError):
        return False, "Invalid max_drawdown value"

    return True, ""


def _save_telemetry(metrics: Dict[str, Any], code: str) -> Path:
    """Save strategy telemetry to disk.

    Args:
        metrics: Strategy performance metrics
        code: Strategy source code

    Returns:
        Path to saved telemetry file
    """
    # Create vault directory if it doesn't exist
    vault_dir = settings.alpha_vault_path
    vault_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    strategy_name = metrics.get("name", "unnamed_strategy")
    safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in strategy_name)
    filename = f"{timestamp}_{safe_name}.json"
    filepath = vault_dir / filename

    # Prepare telemetry data
    telemetry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "code": code,
        "metadata": {
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "status": "validated",
        },
    }

    # Save to file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(telemetry, f, indent=2)

    logger.info(f"Saved strategy telemetry to {filepath}")
    return filepath


async def submit_alpha_telemetry(metrics: Dict[str, Any], code: str) -> List[TextContent]:
    """Submit successful strategy telemetry to the alpha vault.

    This tool accepts performance metrics and code from successful backtests.
    The server validates metrics against minimum thresholds and stores
    qualifying strategies for analysis.

    Args:
        metrics: Dictionary containing strategy performance metrics:
            - sharpe_ratio: Risk-adjusted return metric
            - total_trades: Number of trades executed
            - returns: Total strategy returns
            - max_drawdown: Maximum peak-to-trough decline
            - name: Optional strategy name
            - timeframe: Optional timeframe (e.g., "1D", "1H")
            - win_rate: Optional win rate percentage
        code: Strategy source code (Python)

    Returns:
        List of TextContent with submission confirmation or error
    """
    logger.info("Received alpha telemetry submission")

    # Validate metrics
    is_valid, error_msg = _validate_metrics(metrics)
    if not is_valid:
        logger.warning(f"Telemetry validation failed: {error_msg}")
        return [
            TextContent(
                type="text",
                text=f"Telemetry submission rejected: {error_msg}\n\n"
                f"Minimum requirements:\n"
                f"- Sharpe Ratio: {settings.alpha_vault_min_sharpe}\n"
                f"- Total Trades: {settings.alpha_vault_min_trades}",
            )
        ]

    # Save telemetry
    try:
        filepath = _save_telemetry(metrics, code)

        response_text = (
            f"Alpha telemetry successfully submitted!\n\n"
            f"**Strategy Metrics:**\n"
            f"- Name: {metrics.get('name', 'Unnamed Strategy')}\n"
            f"- Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n"
            f"- Total Trades: {metrics['total_trades']}\n"
            f"- Returns: {float(metrics['returns']):.2%}\n"
            f"- Max Drawdown: {float(metrics['max_drawdown']):.2%}\n"
        )

        if "win_rate" in metrics:
            response_text += f"- Win Rate: {float(metrics['win_rate']):.2%}\n"

        if "timeframe" in metrics:
            response_text += f"- Timeframe: {metrics['timeframe']}\n"

        response_text += f"\n**Saved to:** {filepath.absolute()}\n"
        response_text += f"\nYour strategy has been added to the Alpha Vault for further analysis."

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Failed to save telemetry: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Failed to save telemetry: {str(e)}\n\nPlease contact support if this persists.",
            )
        ]


# Tool definition for MCP protocol
submit_alpha_telemetry_tool = Tool(
    name="submit_alpha_telemetry",
    description=(
        "Submit successful trading strategy telemetry to the Alpha Vault. "
        "Use this after a backtest succeeds and meets performance thresholds. "
        "The server validates metrics (Sharpe ratio >= 1.5, trades >= 100) and stores "
        "qualifying strategies for analysis. This is a RECEIVE-ONLY tool - the server "
        "does NOT execute strategies, only accepts telemetry from client-side backtests."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "metrics": {
                "type": "object",
                "description": "Strategy performance metrics",
                "properties": {
                    "name": {"type": "string", "description": "Strategy name"},
                    "sharpe_ratio": {
                        "type": "number",
                        "description": "Risk-adjusted return metric",
                    },
                    "total_trades": {"type": "integer", "description": "Number of trades executed"},
                    "returns": {
                        "type": "number",
                        "description": "Total strategy returns (e.g., 0.15 for 15%)",
                    },
                    "max_drawdown": {
                        "type": "number",
                        "description": "Maximum peak-to-trough decline (e.g., -0.10 for -10%)",
                    },
                    "win_rate": {
                        "type": "number",
                        "description": "Optional: Win rate percentage (e.g., 0.65 for 65%)",
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Optional: Trading timeframe (e.g., '1D', '1H', '15m')",
                    },
                },
                "required": ["sharpe_ratio", "total_trades", "returns", "max_drawdown"],
            },
            "code": {"type": "string", "description": "Strategy source code (Python)"},
        },
        "required": ["metrics", "code"],
    },
)
