"""
GTI AI
Trading Controller
Version 2.0
"""

from config.settings import Settings
from paper_trading.paper_trading_engine import PaperTradingEngine
from execution.trade_executor import TradeExecutor


class TradingController:
    """
    Coordinates the GTI AI trading workflow.
    """

    def __init__(self):
        self.paper_engine = PaperTradingEngine()
        self.trade_executor = TradeExecutor()

    def run(
        self,
        candles: list,
        balance: float | None = None,
    ) -> dict:
        """
        Execute one complete trading cycle.
        """

        if balance is None:
            balance = Settings.DEFAULT_BALANCE

        result = self.paper_engine.process(
            candles=candles,
            balance=balance,
            risk_percent=Settings.RISK_PERCENT,
            symbol=Settings.SYMBOL,
        )

        if not result.get("success", False):
            return result

        trade = result.get("trade")

        if trade is None:
            return {
                "success": False,
                "message": "No trade generated.",
            }

        if Settings.LIVE_TRADING:
            execution = self.trade_executor.execute(
                symbol=trade["symbol"],
                action=trade["action"],
                volume=trade["volume"],
                entry=trade["entry"],
                stop_loss=trade["stop_loss"],
                take_profit=trade["take_profit"],
            )

            return {
                "success": execution.get("success", False),
                "mode": "LIVE",
                "trade": trade,
                "execution": execution,
            }

        return {
            "success": True,
            "mode": "PAPER",
            "trade": trade,
        }
