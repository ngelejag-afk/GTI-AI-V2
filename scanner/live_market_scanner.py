"""
GTI AI
Live Market Scanner
Version 1.0
"""

from __future__ import annotations

import time

from mt5.mt5_connector import MT5Connector
from mt5.multi_timeframe_reader import MultiTimeframeReader
from analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from analysis.confluence_analyzer import ConfluenceAnalyzer


class LiveMarketScanner:
    """
    Continuously scans the market and generates trading signals.
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

    def scan_once(self) -> dict | None:
        """
        Run one complete market scan.
        """

        market_data = MultiTimeframeReader.read(
            symbol=self.symbol,
            bars=self.bars,
        )

        analysis = MultiTimeframeAnalyzer.analyze(market_data)
        result = ConfluenceAnalyzer.analyze(analysis)

        return {
            "analysis": analysis,
            "signal": result,
        }

    def run(self) -> None:
        """
        Start continuous market monitoring.
        """

        if not self.connector.connect():
            print("❌ Failed to connect to MetaTrader 5.")
            return

        print("====================================")
        print(" GTI AI LIVE MARKET SCANNER")
        print("====================================")
        print(f"Symbol  : {self.symbol}")
        print(f"Refresh : {self.interval} seconds")
        print("Press Ctrl+C to stop.")
        print("====================================")

        try:
            while True:
                result = self.scan_once()

                if result is not None:
                    signal = result["signal"]

                    print("\n------------------------------------")
                    print(f"Decision   : {signal['decision']}")
                    print(f"Confidence : {signal['confidence']}%")
                    print(
                        f"Bullish    : {signal['bullish_votes']}"
                    )
                    print(
                        f"Bearish    : {signal['bearish_votes']}"
                    )

                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nScanner stopped.")

        finally:
            self.connector.disconnect()
