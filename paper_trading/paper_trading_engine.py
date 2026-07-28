"""
GTI AI
Paper Trading Engine
Version 2.0
"""

from analysis.pipeline import AnalysisPipeline
from risk.risk_manager import RiskManager
from strategy.stop_loss_engine import StopLossEngine
from strategy.take_profit_engine import TakeProfitEngine
from journal.trade_journal import TradeJournal


class PaperTradingEngine:
    """
    Simulates live trading without sending real orders.
    """

    def __init__(self):
        self.pipeline = AnalysisPipeline()
        self.journal = TradeJournal()

    def process(
        self,
        candles: list,
        balance: float,
        risk_percent: float = 1.0,
        symbol: str = "XAUUSD",
    ) -> dict:
        """
        Analyze the latest market data and create a paper trade.
        """

        if not candles:
            return {
                "success": False,
                "message": "No candle data.",
            }

        prices = [candle.close for candle in candles]

        result = self.pipeline.analyze(
            prices=prices,
            candles=candles,
        )

        signal = result["signal"]

        if signal["signal"] not in ("BUY", "SELL"):
            return {
                "success": False,
                "message": "No trading signal.",
                "analysis": result,
            }

        entry = candles[-1].close

        stop_loss = StopLossEngine.calculate(
            entry=entry,
            candles=candles,
            trade_type=signal["signal"],
        )

        take_profit = TakeProfitEngine.calculate(
            entry=entry,
            candles=candles,
            trade_type=signal["signal"],
        )

        volume = RiskManager.calculate_lot_size(
            balance=balance,
            risk_percent=risk_percent,
            entry=entry,
            stop_loss=stop_loss,
        )

        trade = {
            "timestamp": str(candles[-1].time),
            "symbol": symbol,
            "action": signal["signal"],
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit["tp1"],
            "volume": volume,
            "status": "OPEN",
        }

        self.journal.log(trade)

        return {
            "success": True,
            "analysis": result,
            "trade": trade,
        }
