"""
GTI AI
Live Market Scanner
Version 2.0
"""

from __future__ import annotations

import time

from analysis.confluence_analyzer import ConfluenceAnalyzer
from analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from execution.trade_executor import TradeExecutor
from mt5.mt5_connector import MT5Connector
from mt5.multi_timeframe_reader import MultiTimeframeReader
from notifications.notification_engine import NotificationEngine
from risk.stop_loss_engine import StopLossEngine
from risk.take_profit_engine import TakeProfitEngine
from web.dashboard_server import DashboardServer


class LiveMarketScanner:
    """
    Continuously scans the live market.
    """

    def __init__(
        self,
        symbol: str = "XAUUSD",
        bars: int = 500,
        interval: int = 5,
    ) -> None:
        self.symbol = symbol
        self.bars = bars
        self.interval = interval
        self.connector = MT5Connector()
        self.last_signal = None

    def scan_once(self) -> dict:
        """
        Perform one market scan.
        """

        market_data = MultiTimeframeReader.read(
            symbol=self.symbol,
            bars=self.bars,
        )

        analysis = MultiTimeframeAnalyzer.analyze(market_data)
        signal = ConfluenceAnalyzer.analyze(analysis)

        timeframe = next(iter(market_data.values()), [])

        if timeframe:
            entry = round(float(timeframe[-1]["close"]), 2)
        else:
            entry = 0.0

        stop_loss = StopLossEngine.calculate(
            entry=entry,
            decision=signal["decision"],
        )

        take_profit = TakeProfitEngine.calculate(
            entry=entry,
            stop_loss=stop_loss,
            decision=signal["decision"],
        )

        signal["symbol"] = self.symbol
        signal["entry"] = entry
        signal["stop_loss"] = stop_loss
        signal["take_profit"] = take_profit

        return signal

    def run(self) -> None:
        """
        Start live scanning.
        """

        if not self.connector.connect():
            print("Unable to connect to MetaTrader 5.")
            return

        print("=" * 50)
        print(" GTI AI LIVE SCANNER")
        print("=" * 50)

        try:
            while True:
                signal = self.scan_once()

                DashboardServer.update(signal)

                decision = signal["decision"]

                if decision != self.last_signal:
                    self.last_signal = decision

                    NotificationEngine.send(signal)

                    if decision in ("BUY", "SELL"):
                        TradeExecutor.execute(signal)

                print()
                print("=" * 50)
                print(" LIVE MARKET SIGNAL")
                print("=" * 50)
                print(f"Symbol        : {self.symbol}")
                print(f"Decision      : {signal['decision']}")
                print(f"Confidence    : {signal['confidence']}%")
                print(f"Entry         : {signal['entry']}")
                print(f"Stop Loss     : {signal['stop_loss']}")
                print(f"Take Profit   : {signal['take_profit']}")
                print("=" * 50)

                print()
                print(f"Open Positions : {len(TradeExecutor.open_positions())}")
                print(f"Trade History  : {len(TradeExecutor.trade_history())}")

                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nLive scanner stopped.")

        finally:
            self.connector.disconnect()
