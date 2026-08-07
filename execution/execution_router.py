from __future__ import annotations
"""
GTI AI
Execution Router
Version 1.0
"""


from config.settings import Settings
from execution.mt5_trade_executor import MT5TradeExecutor
from execution.paper_trading_engine import PaperTradingEngine


class ExecutionRouter:
    """
    Routes trade execution according to
    the configured trading mode.
    """

    @classmethod
    def execute(cls, order: dict) -> dict:
        """
        Execute an order using the configured mode.
        """

        mode = Settings.TRADING_MODE.upper()

        if mode == "PAPER":
            result = PaperTradingEngine.update(
                order=order,
                current_price=order["entry"],
            )

            return {
                "success": True,
                "mode": "PAPER",
                "result": result,
            }

        if mode in ("DEMO", "LIVE"):
            result = MT5TradeExecutor().execute(order)

            result["mode"] = mode

            return result

        return {
            "success": False,
            "mode": mode,
            "message": f"Unsupported trading mode: {mode}",
        }
