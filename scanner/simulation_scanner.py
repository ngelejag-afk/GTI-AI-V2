"""
GTI AI
Simulation Scanner
Version 5.4
"""

from __future__ import annotations

import time

from analysis.pipeline import AnalysisPipeline
from execution.risk_manager import RiskManager
from execution.session_filter import SessionFilter
from execution.signal_adapter import SignalAdapter
from execution.spread_filter import SpreadFilter
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
            "symbol": "",
            "decision": "WAIT",
            "market_bias": "UNKNOWN",
            "entry": 0.0,
            "stop_loss": 0.0,
            "take_profit": 0.0,
            "confidence": 0,
            "lot_size": 0.0,
            "risk_amount": 0.0,
            "risk_reward": "1:0",
            "spread": 0,
            "spread_ok": False,
            "session": "UNKNOWN",
            "session_ok": False,
            "risk_ok": False,
            "trade_allowed": False,
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
                    bid=market["bid"],
                    ask=market["ask"],
                    atr=market["atr"],
                    account_balance=market["account_balance"],
                )

                signal["market_bias"] = result["market"]["market_bias"]
                signal["trade_allowed"] = True

                spread_check = SpreadFilter.validate(
                    spread=market["spread"],
                )

                signal["spread"] = market["spread"]
                signal["spread_ok"] = spread_check["valid"]

                if not spread_check["valid"]:
                    signal["trade_allowed"] = False
                    signal.setdefault("reasons", []).append(
                        spread_check["reason"]
                    )

                session_check = SessionFilter.validate()

                signal["session"] = session_check["session"]
                signal["session_ok"] = session_check["valid"]

                if not session_check["valid"]:
                    signal["trade_allowed"] = False
                    signal.setdefault("reasons", []).append(
                        session_check["reason"]
                    )

                risk_check = RiskManager.validate(
                    open_trades=len(
                        TradeExecutor.open_positions()
                    ),
                )

                signal["risk_ok"] = risk_check["valid"]

                if not risk_check["valid"]:
                    signal["trade_allowed"] = False
                    signal.setdefault("reasons", []).append(
                        risk_check["reason"]
                    )

            DashboardServer.update(signal)

            if signal["decision"] != self.last_decision:
                self.last_decision = signal["decision"]

                NotificationEngine.send(signal)

                if (
                    signal["decision"] in ("BUY", "SELL")
                    and signal.get("trade_allowed", False)
                ):
                    TradeExecutor.execute(signal)

            print()
            print("=" * 60)
            print(" GTI AI SIGNAL")
            print("=" * 60)
            print(f"Decision       : {signal['decision']}")
            print(f"Confidence     : {signal['confidence']}%")
            print(f"Trend          : {signal.get('market_bias', 'UNKNOWN')}")
            print(f"Entry          : {signal['entry']}")
            print(f"Stop Loss      : {signal['stop_loss']}")
            print(f"Take Profit    : {signal['take_profit']}")
            print(f"Lot Size       : {signal.get('lot_size', 0.0)}")
            print(f"Risk Amount    : {signal.get('risk_amount', 0.0)}")
            print(f"Risk Reward    : {signal.get('risk_reward', '-')}")
            print(f"ATR            : {market.get('atr', 0.0)}")
            print(f"Spread         : {market.get('spread', 0)}")
            print(
                f"Spread Status  : "
                f"{'OK' if signal.get('spread_ok', False) else 'BLOCKED'}"
            )
            print(f"Session        : {signal.get('session', 'UNKNOWN')}")
            print(
                f"Session Status : "
                f"{'OK' if signal.get('session_ok', False) else 'BLOCKED'}"
            )
            print(
                f"Risk Status    : "
                f"{'OK' if signal.get('risk_ok', False) else 'BLOCKED'}"
            )
            print(
                f"Trade Allowed  : "
                f"{'YES' if signal.get('trade_allowed', False) else 'NO'}"
            )

            if signal.get("reasons"):
                print("Reasons:")
                for reason in signal["reasons"]:
                    print(f"  - {reason}")

            print(f"Open Positions : {len(TradeExecutor.open_positions())}")
            print(f"Trade History  : {len(TradeExecutor.trade_history())}")
            print("=" * 60)

            time.sleep(self.interval)
