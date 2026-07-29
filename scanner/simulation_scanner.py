"""
GTI AI
Simulation Scanner
Version 4.0
"""

from __future__ import annotations

import time

from analysis.pipeline import AnalysisPipeline
from execution.signal_adapter import SignalAdapter
from execution.trade_executor import TradeExecutor
from execution.trade_lifecycle_manager import TradeLifecycleManager
from mt5.market_data_service import MarketDataService
from notifications.notification_engine import NotificationEngine
from web.dashboard_server import DashboardServer


class SimulationScanner:
    """
    Runs the GTI AI simulation scanner using the AI pipeline.
    """

    def __init__(
        self,
        symbol: str = "XAUUSD",
        interval: int = 5,
    ) -> None:
        self.symbol = symbol
        self.interval = interval
        self.last_decision = None

    @staticmethod
    def _wait_signal() -> dict:
        return {
            "decision": "WAIT",
            "market_bias": "UNKNOWN",
            "entry": 0.0,
            "stop_loss": 0.0,
            "take_profit": 0.0,
            "confidence": 0,
        }

    def run(self) -> None:
        print("=" * 50)
        print(" GTI AI SIMULATION SCANNER")
        print("=" * 50)

        while True:

            market = MarketDataService.get_market_data(
                symbol=self.symbol,
            )

            latest_price = market.get("latest_price")

            if latest_price is not None:
                TradeLifecycleManager.update(
                    positions=TradeExecutor.open_positions(),
                    current_price=latest_price,
                )

            prices = market["close_prices"].get("M15", [])
            candles = market["timeframes"].get("M15", [])

            if not prices or latest_price is None:
                signal = self._wait_signal()

            else:
                result = AnalysisPipeline.analyze(
                    prices=prices,
                    candles=candles,
                    timeframes=market["close_prices"],
                )

                signal = SignalAdapter.adapt(
                    ai_signal=result["signal"],
                    symbol=self.symbol,
                    entry=latest_price,
                )

                signal["market_bias"] = result["market"]["market_bias"]

            DashboardServer.update(signal)

            if signal["decision"] != self.last_decision:
                self.last_decision = signal["decision"]

                NotificationEngine.send(signal)

                if signal["decision"] in ("BUY", "SELL"):
                    TradeExecutor.execute(signal)

            print()
            print("=" * 50)
            print(" GTI AI SIGNAL")
            print("=" * 50)
            print(f"Decision      : {signal['decision']}")
            print(f"Confidence    : {signal['confidence']}%")
            print(f"Trend         : {signal['market_bias']}")
            print(f"Entry         : {signal['entry']}")
            print(f"Stop Loss     : {signal['stop_loss']}")
            print(f"Take Profit   : {signal['take_profit']}")
            print(f"Open Positions: {len(TradeExecutor.open_positions())}")
            print(f"Trade History : {len(TradeExecutor.trade_history())}")
            print("=" * 50)

            time.sleep(self.interval)
