"""
GTI AI
Main Pipeline
Version 2.0
"""

from mt5.mt5_connector import MT5Connector
from mt5.multi_timeframe_reader import MultiTimeframeReader
from analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from analysis.confluence_analyzer import ConfluenceAnalyzer


SYMBOL = "XAUUSD"


def main() -> None:
    connector = MT5Connector()

    if not connector.connect():
        print("❌ Failed to connect to MetaTrader 5.")
        return

    print("✅ Connected to MetaTrader 5")

    market_data = MultiTimeframeReader.read(
        symbol=SYMBOL,
        bars=500,
    )

    analysis = MultiTimeframeAnalyzer.analyze(market_data)

    result = ConfluenceAnalyzer.analyze(analysis)

    print("\n==============================")
    print("GTI AI SIGNAL")
    print("==============================")
    print(f"Symbol      : {SYMBOL}")
    print(f"Decision    : {result['decision']}")
    print(f"Confidence  : {result['confidence']}%")
    print(f"Bullish     : {result['bullish_votes']}")
    print(f"Bearish     : {result['bearish_votes']}")
    print("==============================\n")

    connector.disconnect()


if __name__ == "__main__":
    main()
