"""
GTI AI
Main AI Pipeline
Version 4.0
"""

from mt5.mt5_connector import MT5Connector
from mt5.multi_timeframe_reader import MultiTimeframeReader
from mt5.live_price import LivePriceService

from analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from analysis.confluence_analyzer import ConfluenceAnalyzer
from analysis.smc_analyzer import SMCAnalyzer

from strategy.entry_engine import EntryEngine
from strategy.dynamic_stop_loss import DynamicStopLoss
from strategy.dynamic_take_profit import DynamicTakeProfit

from ai.signal_formatter import SignalFormatter

from news.economic_calendar import EconomicCalendar


SYMBOL = "XAUUSD"


def main() -> None:
    connector = MT5Connector()

    if not connector.connect():
        print("❌ Failed to connect to MT5")
        return

    if not EconomicCalendar.trading_allowed():
        print("🚫 Trading blocked due to high impact news.")
        connector.disconnect()
        return

    market = MultiTimeframeReader.read(
        symbol=SYMBOL,
        bars=500,
    )

    analysis = MultiTimeframeAnalyzer.analyze(market)

    confluence = ConfluenceAnalyzer.analyze(analysis)

    decision = confluence["decision"]

    if decision == "WAIT":
        print("⏳ WAIT")
        connector.disconnect()
        return

    price = LivePriceService.get(SYMBOL)

    if price is None:
        print("❌ Live price unavailable.")
        connector.disconnect()
        return

    entry = EntryEngine.calculate(
        decision=decision,
        bid=price["bid"],
        ask=price["ask"],
    )

    smc = SMCAnalyzer.analyze(
        market["M15"],
    )

    stop_loss = DynamicStopLoss.calculate(
        decision=decision,
        entry=entry,
        candles=market["M15"],
    )

    take_profit = DynamicTakeProfit.calculate(
        decision=decision,
        entry=entry,
        candles=market["M15"],
    )

    confidence = min(
        100,
        confluence["confidence"] + (smc["score"] // 5),
    )

    signal = SignalFormatter.format(
        symbol=SYMBOL,
        action=decision,
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
        confidence=confidence,
    )

    print(signal)

    connector.disconnect()


if __name__ == "__main__":
    main()
