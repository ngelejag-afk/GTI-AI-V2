"""
GTI AI
Live Market Scanner
Version 1.1
"""

from __future__ import annotations

import time

from analysis.confluence_analyzer import ConfluenceAnalyzer
from analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from mt5.mt5_connector import MT5Connector
from mt5.multi_timeframe_reader import MultiTimeframeReader


class LiveMarketScanner:
    """
    Continuously scans the market and reports only new signals.
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
        Execute one market scan.
        """

        market_data = MultiTimeframeReader.read(
            symbol=self.symbol,
            bars=self.bars,
        )

        analysis = MultiTimeframeAnalyzer.analyze(market_data)
        signal = ConfluenceAnalyzer.analyze(analysis)

        return signal

    def run(self) -> None:
        """
        Start continuous scanning.
        """

        if not self.connector.connect():
            print("❌ Unable to connect to MetaTrader 5.")
            return

        print("=" * 45)
        print(" GTI AI LIVE MARKET SCANNER")
        print("=" * 45)
        print(f"Symbol   : {self.symbol}")
        print(f"Refresh  : {self.interval} seconds")
        print("Press Ctrl+C to stop.")
        print("=" * 45)

        try:
            while True:
                signal = self.scan_once()

                decision = signal["decision"]

                if decision != self.last_signal:
                    self.last_signal = decision

                    print()
                    print("=" * 45)
                    print(" NEW MARKET SIGNAL")
                    print("=" * 45)
                    print(f"Decision   : {decision}")
                    print(f"Confidence : {signal['confidence']}%")
                    print(f"Bullish    : {signal['bullish_votes']}")
                    print(f"Bearish    : {signal['bearish_votes']}")
                    print("=" * 45)

                else:
                    print(f"No signal change ({decision})")

                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nScanner stopped.")

        finally:
            self.connector.disconnect()
