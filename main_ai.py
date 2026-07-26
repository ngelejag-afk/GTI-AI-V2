"""
GTI AI
Main AI Pipeline
Version 3.0
"""

from mt5.mt5_connector import MT5Connector
from mt5.multi_timeframe_reader import MultiTimeframeReader
from analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from analysis.confluence_analyzer import ConfluenceAnalyzer
from mt5.live_price import LivePriceService
from strategy.entry_engine import EntryEngine
from strategy.stop_loss_engine import StopLossEngine
from strategy.take_profit_engine import TakeProfitEngine
from ai.signal_formatter import SignalFormatter


SYMBOL = "XAUUSD"


def main() -> None:
    connector = MT5Connector()

    if not connector.connect():
        print("❌ Failed to connect to MetaTrader 5.")
        return

    market = MultiTimeframeReader.read(
        symbol=SYMBOL,
        bars=500,
    )

    analysis = MultiTimeframeAnalyzer.analyze(market)

    result = ConfluenceAnalyzer.analyze(analysis)

    decision = result["decision"]

    if decision == "WAIT":
        print("⏳ No trading opportunity.")
        connector.disconnect()
        return

    price = LivePriceService.get(SYMBOL)

    if price is None:
        print("❌ Failed to read live price.")
        connector.disconnect()
        return

    entry = EntryEngine.calculate(
        decision=decision,
        bid=price["bid"],
        ask=price["ask"],
    )

    stop_loss = StopLossEngine.calculate(
        decision=decision,
        entry=entry,
    )

    take_profit = TakeProfitEngine.calculate(
        decision=decision,
        entry=entry,
        stop_loss=stop_loss,
    )

    signal = SignalFormatter.format(
        symbol=SYMBOL,
        action=decision,
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
        confidence=result["confidence"],
    )

    print(signal)

    connector.disconnect()


if __name__ == "__main__":
    main()
