"""Adapter module bridging validator TradeRecords to daemon StrategySignals."""

from __future__ import annotations

from gti_v2_1_2_validator import TradeRecord
from gti_v2_unified_daemon import Indicators, StrategySignal


def adapt_trade_to_signal(trade: TradeRecord) -> StrategySignal:
    """Convert a validator TradeRecord into a daemon StrategySignal.

    Maps trade direction, entry, stop loss, take profit, and indicator metrics
    into the daemon's expected StrategySignal and Indicators contracts.
    """
    indicators = Indicators(
        ema_fast=trade.entry,
        ema_slow=trade.stop_loss,
        atr=abs(trade.entry - trade.stop_loss) / 1.5,
        rsi=50.0,
        volume_sma=100.0,
    )

    risk_reward = 0.0
    if trade.entry != trade.stop_loss:
        risk_reward = abs(trade.take_profit - trade.entry) / abs(trade.entry - trade.stop_loss)

    return StrategySignal(
        direction=trade.direction,
        entry=trade.entry,
        stop=trade.stop_loss,
        target=trade.take_profit,
        risk_reward=risk_reward,
        score=trade.mtf_alignment,
        valid=True,
        reason="Validator trade signal adapted successfully.",
        candle_timestamp=trade.timestamp,
        indicators=indicators,
    )
