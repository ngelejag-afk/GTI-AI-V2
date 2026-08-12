from __future__ import annotations

import argparse
import csv
import json
import math
import time
from bisect import bisect_right
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import requests


CANDLE_API = (
    "https://api.exchange.coinbase.com/"
    "products/BTC-USD/candles"
)

REQUEST_TIMEOUT = 15
CANDLE_GRANULARITY = 300

M5_SECONDS = 5 * 60
M15_SECONDS = 15 * 60
H1_SECONDS = 60 * 60
H4_SECONDS = 4 * 60 * 60
D1_SECONDS = 24 * 60 * 60

EMA_FAST = 20
EMA_SLOW = 50
ATR_PERIOD = 14

SL_ATR_MULTIPLIER = 1.5
TP_R_MULTIPLE = 2.0

NEWS_BLOCK_THRESHOLD = 5
NEWS_LOOKBACK_MINUTES = 30
NEWS_LOOKAHEAD_MINUTES = 120

MAJOR_NEWS_KEYWORDS = (
    "fomc",
    "fed",
    "federal reserve",
    "interest rate",
    "rate decision",
    "cpi",
    "consumer price",
    "nfp",
    "non-farm",
    "nonfarm",
    "pce",
    "personal consumption",
    "gdp",
    "employment",
    "unemployment",
    "powell",
    "fed chair",
)

SUPPORTED_STRATEGIES = (
    "A_TECH_ONLY",
    "B_MTF_ONLY",
    "C_MTF_NEWS",
)


@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class NewsEvent:
    timestamp: int
    currency: str
    impact: str
    title: str
    actual: Optional[str]
    forecast: Optional[str]
    previous: Optional[str]


@dataclass(frozen=True)
class TimeframeState:
    trend: str
    ema20: Optional[float]
    ema50: Optional[float]


@dataclass(frozen=True)
class MTFState:
    m5: TimeframeState
    m15: TimeframeState
    h1: TimeframeState
    h4: TimeframeState
    d1: TimeframeState
    alignment_score: int


@dataclass(frozen=True)
class NewsRisk:
    score: int
    category: str
    nearest_event: Optional[NewsEvent]
    minutes_to_event: Optional[float]


@dataclass(frozen=True)
class Signal:
    timestamp: int
    direction: str
    score: int
    mtf: MTFState
    news: NewsRisk


@dataclass
class TradeRecord:
    timestamp: int
    strategy: str
    direction: str
    entry: float
    stop_loss: float
    take_profit: float
    exit_timestamp: int
    exit_price: float
    result: str
    pnl_r: float
    news_risk: int
    mtf_alignment: int


@dataclass(frozen=True)
class Performance:
    strategy: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    net_r: float
    expectancy_r: float
    profit_factor: float
    max_drawdown_r: float
    max_consecutive_losses: int


@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def get_json(
    url: str,
    params: Optional[Dict[str, str]] = None,
) -> object:
    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent": "GTI-AI-V2-1.2",
        },
    )
    response.raise_for_status()
    return response.json()


def fetch_m5_candles(
    start_timestamp: int,
    end_timestamp: int,
) -> List[Candle]:
    max_seconds = CANDLE_GRANULARITY * 299
    cursor = start_timestamp
    candles: Dict[int, Candle] = {}

    while cursor < end_timestamp:
        chunk_end = min(
            cursor + max_seconds,
            end_timestamp,
        )

        payload = get_json(
            CANDLE_API,
            {
                "start": str(cursor),
                "end": str(chunk_end),
                "granularity": str(
                    CANDLE_GRANULARITY
                ),
            },
        )

        if not isinstance(payload, list):
            raise RuntimeError(
                "Coinbase returned an unexpected candle response."
            )

        for item in payload:
            if not isinstance(item, list):
                continue

            if len(item) < 6:
                continue

            candle = Candle(
                timestamp=int(item[0]),
                low=float(item[1]),
                high=float(item[2]),
                open=float(item[3]),
                close=float(item[4]),
                volume=float(item[5]),
            )

            candles[candle.timestamp] = candle

        cursor = chunk_end + CANDLE_GRANULARITY
        time.sleep(0.15)

    return sorted(
        candles.values(),
        key=lambda candle: candle.timestamp,
    )


def aggregate_candles(
    candles: Sequence[Candle],
    timeframe_seconds: int,
) -> List[Candle]:
    if timeframe_seconds == M5_SECONDS:
        return list(candles)

    buckets: Dict[int, List[Candle]] = {}

    for candle in candles:
        bucket_timestamp = (
            candle.timestamp
            - candle.timestamp % timeframe_seconds
        )

        buckets.setdefault(
            bucket_timestamp,
            [],
        ).append(candle)

    result: List[Candle] = []

    for timestamp, bucket in sorted(
        buckets.items()
    ):
        bucket.sort(
            key=lambda candle: candle.timestamp
        )

        result.append(
            Candle(
                timestamp=timestamp,
                open=bucket[0].open,
                high=max(
                    candle.high
                    for candle in bucket
                ),
                low=min(
                    candle.low
                    for candle in bucket
                ),
                close=bucket[-1].close,
                volume=sum(
                    candle.volume
                    for candle in bucket
                ),
            )
        )

    return result


def ema_series(
    values: Sequence[float],
    period: int,
) -> List[Optional[float]]:
    result: List[Optional[float]] = [
        None
    ] * len(values)

    if len(values) < period:
        return result

    current = (
        sum(values[:period])
        / period
    )

    result[period - 1] = current

    multiplier = 2.0 / (period + 1)

    for index in range(
        period,
        len(values),
    ):
        current = (
            values[index] - current
        ) * multiplier + current

        result[index] = current

    return result


def atr_series(
    candles: Sequence[Candle],
    period: int,
) -> List[Optional[float]]:
    result: List[Optional[float]] = [
        None
    ] * len(candles)

    if len(candles) <= period:
        return result

    true_ranges: List[float] = []

    for index in range(1, len(candles)):
        current = candles[index]
        previous = candles[index - 1]

        true_ranges.append(
            max(
                current.high - current.low,
                abs(
                    current.high
                    - previous.close
                ),
                abs(
                    current.low
                    - previous.close
                ),
            )
        )

    atr = (
        sum(true_ranges[:period])
        / period
    )

    result[period] = atr

    for index in range(
        period + 1,
        len(candles),
    ):
        true_range = true_ranges[index - 1]

        atr = (
            atr * (period - 1)
            + true_range
        ) / period

        result[index] = atr

    return result


def build_timeframe_states(
    candles: Sequence[Candle],
) -> List[TimeframeState]:
    closes = [
        candle.close
        for candle in candles
    ]

    ema20 = ema_series(
        closes,
        EMA_FAST,
    )

    ema50 = ema_series(
        closes,
        EMA_SLOW,
    )

    states: List[TimeframeState] = []

    for index in range(len(candles)):
        fast = ema20[index]
        slow = ema50[index]

        if fast is None or slow is None:
            states.append(
                TimeframeState(
                    trend="UNKNOWN",
                    ema20=fast,
                    ema50=slow,
                )
            )
            continue

        price = candles[index].close

        if price > fast > slow:
            trend = "BULLISH"

        elif price < fast < slow:
            trend = "BEARISH"

        else:
            trend = "CONSOLIDATION"

        states.append(
            TimeframeState(
                trend=trend,
                ema20=fast,
                ema50=slow,
            )
        )

    return states


@dataclass
class PreparedMarket:
    m5: List[Candle]
    m15: List[Candle]
    h1: List[Candle]
    h4: List[Candle]
    d1: List[Candle]

    m5_states: List[TimeframeState]
    m15_states: List[TimeframeState]
    h1_states: List[TimeframeState]
    h4_states: List[TimeframeState]
    d1_states: List[TimeframeState]

    m15_atr: List[Optional[float]]

    m15_timestamps: List[int]
    h1_timestamps: List[int]
    h4_timestamps: List[int]
    d1_timestamps: List[int]


def prepare_market(
    m5: Sequence[Candle],
) -> PreparedMarket:
    m5_list = list(m5)

    m15 = aggregate_candles(
        m5_list,
        M15_SECONDS,
    )

    h1 = aggregate_candles(
        m5_list,
        H1_SECONDS,
    )

    h4 = aggregate_candles(
        m5_list,
        H4_SECONDS,
    )

    d1 = aggregate_candles(
        m5_list,
        D1_SECONDS,
    )

    return PreparedMarket(
        m5=m5_list,
        m15=m15,
        h1=h1,
        h4=h4,
        d1=d1,
        m5_states=build_timeframe_states(
            m5_list
        ),
        m15_states=build_timeframe_states(
            m15
        ),
        h1_states=build_timeframe_states(
            h1
        ),
        h4_states=build_timeframe_states(
            h4
        ),
        d1_states=build_timeframe_states(
            d1
        ),
        m15_atr=atr_series(
            m15,
            ATR_PERIOD,
        ),
        m15_timestamps=[
            candle.timestamp
            for candle in m15
        ],
        h1_timestamps=[
            candle.timestamp
            for candle in h1
        ],
        h4_timestamps=[
            candle.timestamp
            for candle in h4
        ],
        d1_timestamps=[
            candle.timestamp
            for candle in d1
        ],
    )


def latest_completed_state(
    candles: Sequence[Candle],
    states: Sequence[TimeframeState],
    timestamps: Sequence[int],
    decision_timestamp: int,
    timeframe_seconds: int,
) -> TimeframeState:
    completed_timestamp = (
        decision_timestamp
        - timeframe_seconds
    )

    position = bisect_right(
        timestamps,
        completed_timestamp,
    ) - 1

    if position < 0:
        return TimeframeState(
            trend="UNKNOWN",
            ema20=None,
            ema50=None,
        )

    if position >= len(states):
        position = len(states) - 1

    return states[position]


def build_mtf_state(
    market: PreparedMarket,
    decision_timestamp: int,
) -> MTFState:
    m5_state = latest_completed_state(
        market.m5,
        market.m5_states,
        [
            candle.timestamp
            for candle in market.m5
        ],
        decision_timestamp,
        M5_SECONDS,
    )

    m15_state = latest_completed_state(
        market.m15,
        market.m15_states,
        market.m15_timestamps,
        decision_timestamp,
        M15_SECONDS,
    )

    h1_state = latest_completed_state(
        market.h1,
        market.h1_states,
        market.h1_timestamps,
        decision_timestamp,
        H1_SECONDS,
    )

    h4_state = latest_completed_state(
        market.h4,
        market.h4_states,
        market.h4_timestamps,
        decision_timestamp,
        H4_SECONDS,
    )

    d1_state = latest_completed_state(
        market.d1,
        market.d1_states,
        market.d1_timestamps,
        decision_timestamp,
        D1_SECONDS,
    )

    trends = (
        m5_state.trend,
        m15_state.trend,
        h1_state.trend,
        h4_state.trend,
        d1_state.trend,
    )

    alignment_score = sum(
        1
        if trend == "BULLISH"
        else -1
        if trend == "BEARISH"
        else 0
        for trend in trends
    )

    return MTFState(
        m5=m5_state,
        m15=m15_state,
        h1=h1_state,
        h4=h4_state,
        d1=d1_state,
        alignment_score=alignment_score,
    )


def parse_timestamp(value: object) -> Optional[int]:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return int(value)

    text = str(value).strip()

    if not text:
        return None

    formats = (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    )

    for fmt in formats:
        try:
            parsed = datetime.strptime(
                text,
                fmt,
            )

            if parsed.tzinfo is None:
                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            return int(
                parsed.timestamp()
            )

        except ValueError:
            continue

    return None


def normalize_news_item(
    item: Dict[str, object],
) -> Optional[NewsEvent]:
    timestamp = parse_timestamp(
        item.get("date")
        or item.get("timestamp")
    )

    if timestamp is None:
        return None

    currency = str(
        item.get("currency", "")
    ).upper().strip()

    impact = str(
        item.get("impact", "")
    ).strip()

    title = str(
        item.get("title")
        or item.get("event")
        or ""
    ).strip()

    if not currency or not title:
        return None

    return NewsEvent(
        timestamp=timestamp,
        currency=currency,
        impact=impact,
        title=title,
        actual=(
            str(item["actual"])
            if item.get("actual") is not None
            else None
        ),
        forecast=(
            str(item["forecast"])
            if item.get("forecast") is not None
            else None
        ),
        previous=(
            str(item["previous"])
            if item.get("previous") is not None
            else None
        ),
    )


def parse_news_payload(
    payload: object,
) -> List[NewsEvent]:
    if isinstance(payload, dict):
        if "events" in payload:
            payload = payload["events"]
        elif "calendar" in payload:
            payload = payload["calendar"]
        else:
            payload = [payload]

    if not isinstance(payload, list):
        raise ValueError(
            "Unsupported news JSON structure."
        )

    events: List[NewsEvent] = []

    for item in payload:
        if not isinstance(item, dict):
            continue

        event = normalize_news_item(item)

        if event is not None:
            events.append(event)

    return sorted(
        events,
        key=lambda event: event.timestamp,
    )


def load_news_file(
    filename: str,
) -> List[NewsEvent]:
    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(
            f"News file does not exist: {filename}"
        )

    if path.suffix.lower() == ".csv":
        return load_news_csv(path)

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        payload = json.load(file)

    return parse_news_payload(payload)


def load_news_csv(
    path: Path,
) -> List[NewsEvent]:
    events: List[NewsEvent] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            item: Dict[str, object] = {
                "date": row.get("date"),
                "currency": row.get("currency"),
                "impact": row.get("impact"),
                "title": (
                    row.get("event")
                    or row.get("title")
                ),
                "actual": row.get("actual"),
                "forecast": row.get("forecast"),
                "previous": row.get("previous"),
            }

            event = normalize_news_item(
                item
            )

            if event is not None:
                events.append(event)

    return sorted(
        events,
        key=lambda event: event.timestamp,
    )


def news_category(
    score: int,
) -> str:
    if score <= 0:
        return "None"

    if score <= 2:
        return "Low"

    if score <= 4:
        return "Elevated"

    if score <= 6:
        return "High"

    if score <= 8:
        return "Very High"

    return "Extreme"


def evaluate_news_risk(
    current_timestamp: int,
    events: Sequence[NewsEvent],
) -> NewsRisk:
    nearest: Optional[NewsEvent] = None
    nearest_distance: Optional[float] = None

    for event in events:
        if event.currency != "USD":
            continue

        distance_minutes = (
            event.timestamp
            - current_timestamp
        ) / 60.0

        if (
            -NEWS_LOOKBACK_MINUTES
            <= distance_minutes
            <= NEWS_LOOKAHEAD_MINUTES
        ):
            if (
                nearest_distance is None
                or abs(distance_minutes)
                < abs(nearest_distance)
            ):
                nearest = event
                nearest_distance = (
                    distance_minutes
                )

    if nearest is None:
        return NewsRisk(
            score=0,
            category="None",
            nearest_event=None,
            minutes_to_event=None,
        )

    impact = nearest.impact.lower()
    title = nearest.title.lower()

    score = 0

    if impact == "high":
        score += 5
    elif impact == "medium":
        score += 2
    elif impact == "low":
        score += 1

    if any(
        keyword in title
        for keyword in MAJOR_NEWS_KEYWORDS
    ):
        score += 3

    if nearest_distance is not None:
        if abs(nearest_distance) <= 15:
            score += 2
        elif abs(nearest_distance) >= 60:
            score -= 1

    score = max(
        0,
        min(10, score),
    )

    return NewsRisk(
        score=score,
        category=news_category(score),
        nearest_event=nearest,
        minutes_to_event=nearest_distance,
    )


def get_m15_signal(
    market: PreparedMarket,
    m15_index: int,
) -> Optional[Signal]:
    if m15_index < 1:
        return None

    if m15_index >= len(market.m15):
        return None

    current = market.m15[m15_index]
    previous = market.m15[m15_index - 1]

    current_fast = market.m15_states[
        m15_index
    ].ema20

    current_slow = market.m15_states[
        m15_index
    ].ema50

    previous_fast = market.m15_states[
        m15_index - 1
    ].ema20

    previous_slow = market.m15_states[
        m15_index - 1
    ].ema50

    if (
        current_fast is None
        or current_slow is None
        or previous_fast is None
        or previous_slow is None
    ):
        return None

    direction: Optional[str] = None

    bullish_cross = (
        previous_fast <= previous_slow
        and current_fast > current_slow
    )

    bearish_cross = (
        previous_fast >= previous_slow
        and current_fast < current_slow
    )

    if bullish_cross:
        direction = "BUY"

    elif bearish_cross:
        direction = "SELL"

    if direction is None:
        return None

    decision_timestamp = (
        current.timestamp
        + M15_SECONDS
    )

    mtf = build_mtf_state(
        market,
        decision_timestamp,
    )

    return Signal(
        timestamp=decision_timestamp,
        direction=direction,
        score=mtf.alignment_score,
        mtf=mtf,
        news=NewsRisk(
            score=0,
            category="None",
            nearest_event=None,
            minutes_to_event=None,
        ),
    )


def apply_news_to_signal(
    signal: Signal,
    events: Sequence[NewsEvent],
) -> Signal:
    news = evaluate_news_risk(
        signal.timestamp,
        events,
    )

    return Signal(
        timestamp=signal.timestamp,
        direction=signal.direction,
        score=signal.score,
        mtf=signal.mtf,
        news=news,
    )


def strategy_allows_signal(
    signal: Signal,
    strategy: str,
) -> bool:
    if strategy not in SUPPORTED_STRATEGIES:
        raise ValueError(
            f"Unsupported strategy: {strategy}"
        )

    if strategy == "A_TECH_ONLY":
        return True

    direction_sign = (
        1
        if signal.direction == "BUY"
        else -1
    )

    if strategy in (
        "B_MTF_ONLY",
        "C_MTF_NEWS",
    ):
        h1 = signal.mtf.h1.trend
        h4 = signal.mtf.h4.trend

        required = (
            "BULLISH"
            if direction_sign == 1
            else "BEARISH"
        )

        if h1 != required or h4 != required:
            return False

    if strategy == "C_MTF_NEWS":
        if (
            signal.news.score
            >= NEWS_BLOCK_THRESHOLD
        ):
            return False

    return True


def find_m5_index_at_or_after(
    market: PreparedMarket,
    timestamp: int,
) -> Optional[int]:
    timestamps = [
        candle.timestamp
        for candle in market.m5
    ]

    index = bisect_right(
        timestamps,
        timestamp - 1,
    )

    if index >= len(market.m5):
        return None

    return index


def simulate_trade(
    market: PreparedMarket,
    entry_index: int,
    direction: str,
    entry: float,
    stop_loss: float,
    take_profit: float,
) -> Optional[Tuple[str, float, int]]:
    for index in range(
        entry_index,
        len(market.m5),
    ):
        candle = market.m5[index]

        if direction == "BUY":
            stop_hit = (
                candle.low <= stop_loss
            )

            target_hit = (
                candle.high >= take_profit
            )

        else:
            stop_hit = (
                candle.high >= stop_loss
            )

            target_hit = (
                candle.low <= take_profit
            )

        if stop_hit and target_hit:
            return (
                "LOSS",
                -1.0,
                candle.timestamp,
            )

        if stop_hit:
            return (
                "LOSS",
                -1.0,
                candle.timestamp,
            )

        if target_hit:
            return (
                "WIN",
                TP_R_MULTIPLE,
                candle.timestamp,
            )

    return None


def run_strategy(
    market: PreparedMarket,
    events: Sequence[NewsEvent],
    strategy: str,
    start_timestamp: int,
    end_timestamp: int,
) -> List[TradeRecord]:
    trades: List[TradeRecord] = []

    m15_indices = range(
        len(market.m15)
    )

    occupied_until = start_timestamp

    for m15_index in m15_indices:
        candle = market.m15[m15_index]

        decision_timestamp = (
            candle.timestamp
            + M15_SECONDS
        )

        if decision_timestamp < start_timestamp:
            continue

        if decision_timestamp >= end_timestamp:
            break

        if decision_timestamp < occupied_until:
            continue

        signal = get_m15_signal(
            market,
            m15_index,
        )

        if signal is None:
            continue

        signal = apply_news_to_signal(
            signal,
            events,
        )

        if not strategy_allows_signal(
            signal,
            strategy,
        ):
            continue

        atr = market.m15_atr[
            m15_index
        ]

        if atr is None or atr <= 0:
            continue

        entry_index = find_m5_index_at_or_after(
            market,
            decision_timestamp,
        )

        if entry_index is None:
            continue

        entry_candle = market.m5[
            entry_index
        ]

        entry = entry_candle.open
        sl_distance = (
            atr * SL_ATR_MULTIPLIER
        )

        if signal.direction == "BUY":
            stop_loss = (
                entry - sl_distance
            )
            take_profit = (
                entry
                + sl_distance
                * TP_R_MULTIPLE
            )

        else:
            stop_loss = (
                entry + sl_distance
            )
            take_profit = (
                entry
                - sl_distance
                * TP_R_MULTIPLE
            )

        outcome = simulate_trade(
            market,
            entry_index,
            signal.direction,
            entry,
            stop_loss,
            take_profit,
        )

        if outcome is None:
            continue

        result, pnl_r, exit_timestamp = (
            outcome
        )

        exit_price = (
            take_profit
            if result == "WIN"
            else stop_loss
        )

        trades.append(
            TradeRecord(
                timestamp=decision_timestamp,
                strategy=strategy,
                direction=signal.direction,
                entry=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                exit_timestamp=exit_timestamp,
                exit_price=exit_price,
                result=result,
                pnl_r=pnl_r,
                news_risk=signal.news.score,
                mtf_alignment=(
                    signal.mtf.alignment_score
                ),
            )
        )

        occupied_until = (
            exit_timestamp + 1
        )

    return trades


def calculate_max_drawdown(
    trades: Sequence[TradeRecord],
) -> float:
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0

    for trade in trades:
        equity += trade.pnl_r
        peak = max(peak, equity)

        drawdown = peak - equity
        max_drawdown = max(
            max_drawdown,
            drawdown,
        )

    return max_drawdown


def calculate_max_consecutive_losses(
    trades: Sequence[TradeRecord],
) -> int:
    current = 0
    maximum = 0

    for trade in trades:
        if trade.result == "LOSS":
            current += 1
            maximum = max(
                maximum,
                current,
            )
        else:
            current = 0

    return maximum


def performance(
    strategy: str,
    trades: Sequence[TradeRecord],
) -> Performance:
    wins = [
        trade
        for trade in trades
        if trade.result == "WIN"
    ]

    losses = [
        trade
        for trade in trades
        if trade.result == "LOSS"
    ]

    net_r = sum(
        trade.pnl_r
        for trade in trades
    )

    gross_profit = sum(
        trade.pnl_r
        for trade in trades
        if trade.pnl_r > 0
    )

    gross_loss = abs(
        sum(
            trade.pnl_r
            for trade in trades
            if trade.pnl_r < 0
        )
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else math.inf
    )

    trade_count = len(trades)

    win_rate = (
        len(wins) / trade_count * 100
        if trade_count
        else 0.0
    )

    expectancy = (
        net_r / trade_count
        if trade_count
        else 0.0
    )

    return Performance(
        strategy=strategy,
        trades=trade_count,
        wins=len(wins),
        losses=len(losses),
        win_rate=win_rate,
        net_r=net_r,
        expectancy_r=expectancy,
        profit_factor=profit_factor,
        max_drawdown_r=calculate_max_drawdown(
            trades
        ),
        max_consecutive_losses=(
            calculate_max_consecutive_losses(
                trades
            )
        ),
    )


def print_performance(
    report: Performance,
) -> None:
    profit_factor = (
        "INF"
        if math.isinf(report.profit_factor)
        else f"{report.profit_factor:.2f}"
    )

    print()
    print(
        f"[{report.strategy}]"
    )
    print(
        f"Trades              : {report.trades}"
    )
    print(
        f"Wins / Losses       : "
        f"{report.wins} / {report.losses}"
    )
    print(
        f"Win Rate            : "
        f"{report.win_rate:.2f}%"
    )
    print(
        f"Net R               : "
        f"{report.net_r:.2f}R"
    )
    print(
        f"Expectancy          : "
        f"{report.expectancy_r:.4f}R"
    )
    print(
        f"Profit Factor       : "
        f"{profit_factor}"
    )
    print(
        f"Max Drawdown        : "
        f"{report.max_drawdown_r:.2f}R"
    )
    print(
        f"Max Consecutive Ls  : "
        f"{report.max_consecutive_losses}"
    )


def build_walk_forward_windows(
    start_timestamp: int,
    end_timestamp: int,
    train_days: int,
    test_days: int,
) -> List[WalkForwardWindow]:
    train_seconds = (
        train_days * 86400
    )

    test_seconds = (
        test_days * 86400
    )

    windows: List[WalkForwardWindow] = []

    cursor = (
        start_timestamp
        + train_seconds
    )

    while cursor + test_seconds <= end_timestamp:
        windows.append(
            WalkForwardWindow(
                train_start=(
                    cursor - train_seconds
                ),
                train_end=cursor,
                test_start=cursor,
                test_end=(
                    cursor + test_seconds
                ),
            )
        )

        cursor += test_seconds

    return windows


def run_walk_forward(
    market: PreparedMarket,
    events: Sequence[NewsEvent],
    start_timestamp: int,
    end_timestamp: int,
    train_days: int,
    test_days: int,
) -> Dict[str, List[TradeRecord]]:
    windows = build_walk_forward_windows(
        start_timestamp,
        end_timestamp,
        train_days,
        test_days,
    )

    if not windows:
        raise ValueError(
            "Not enough data for the requested "
            "walk-forward train/test windows."
        )

    out_of_sample: Dict[
        str,
        List[TradeRecord]
    ] = {
        strategy: []
        for strategy in SUPPORTED_STRATEGIES
    }

    print()
    print(
        "========================================="
    )
    print(
        " WALK-FORWARD VALIDATION"
    )
    print(
        "========================================="
    )

    for number, window in enumerate(
        windows,
        start=1,
    ):
        train_start = datetime.fromtimestamp(
            window.train_start,
            timezone.utc,
        ).strftime("%Y-%m-%d")

        train_end = datetime.fromtimestamp(
            window.train_end,
            timezone.utc,
        ).strftime("%Y-%m-%d")

        test_start = datetime.fromtimestamp(
            window.test_start,
            timezone.utc,
        ).strftime("%Y-%m-%d")

        test_end = datetime.fromtimestamp(
            window.test_end,
            timezone.utc,
        ).strftime("%Y-%m-%d")

        print()
        print(
            f"Window {number}: "
            f"TRAIN {train_start} → {train_end} | "
            f"TEST {test_start} → {test_end}"
        )

        for strategy in SUPPORTED_STRATEGIES:
            test_trades = run_strategy(
                market=market,
                events=events,
                strategy=strategy,
                start_timestamp=window.test_start,
                end_timestamp=window.test_end,
            )

            out_of_sample[
                strategy
            ].extend(test_trades)

            report = performance(
                strategy,
                test_trades,
            )

            print(
                f"  {strategy}: "
                f"{report.trades} trades | "
                f"{report.win_rate:.1f}% WR | "
                f"{report.net_r:.2f}R"
            )

    return out_of_sample


def save_trades(
    filename: str,
    trades: Iterable[TradeRecord],
) -> None:
    path = Path(filename)

    fields = [
        "timestamp",
        "strategy",
        "direction",
        "entry",
        "stop_loss",
        "take_profit",
        "exit_timestamp",
        "exit_price",
        "result",
        "pnl_r",
        "news_risk",
        "mtf_alignment",
    ]

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for trade in trades:
            writer.writerow(
                {
                    "timestamp": trade.timestamp,
                    "strategy": trade.strategy,
                    "direction": trade.direction,
                    "entry": f"{trade.entry:.2f}",
                    "stop_loss": (
                        f"{trade.stop_loss:.2f}"
                    ),
                    "take_profit": (
                        f"{trade.take_profit:.2f}"
                    ),
                    "exit_timestamp": (
                        trade.exit_timestamp
                    ),
                    "exit_price": (
                        f"{trade.exit_price:.2f}"
                    ),
                    "result": trade.result,
                    "pnl_r": f"{trade.pnl_r:.4f}",
                    "news_risk": trade.news_risk,
                    "mtf_alignment": (
                        trade.mtf_alignment
                    ),
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "GTI-AI-V2-1.2 BTCUSD "
            "walk-forward validator."
        )
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help=(
            "Outright test data span in days. "
            "Warm-up is added automatically."
        ),
    )

    parser.add_argument(
        "--walk-forward-train",
        type=int,
        default=30,
        help="Training window size in days.",
    )

    parser.add_argument(
        "--walk-forward-test",
        type=int,
        default=7,
        help="Out-of-sample test window in days.",
    )

    parser.add_argument(
        "--news-file",
        type=str,
        default=None,
        help=(
            "Historical Forex Factory JSON or CSV."
        ),
    )

    parser.add_argument(
        "--output",
        type=str,
        default="gti_v2_1_2_oos_trades.csv",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.days <= 0:
        raise ValueError(
            "--days must be greater than zero."
        )

    if args.walk_forward_train <= 0:
        raise ValueError(
            "--walk-forward-train must be "
            "greater than zero."
        )

    if args.walk_forward_test <= 0:
        raise ValueError(
            "--walk-forward-test must be "
            "greater than zero."
        )

    now = int(time.time())

    test_span = (
        args.days * 86400
    )

    end_timestamp = now

    requested_start = (
        end_timestamp - test_span
    )

    warmup_days = max(
        args.walk_forward_train,
        60,
    )

    download_start = (
        requested_start
        - warmup_days * 86400
    )

    print(
        "========================================="
    )
    print(
        " GTI-AI-V2-1.2 VALIDATION ENGINE"
    )
    print(
        "========================================="
    )
    print(
        f"Test span       : {args.days} days"
    )
    print(
        f"Walk-forward    : "
        f"{args.walk_forward_train}d train / "
        f"{args.walk_forward_test}d test"
    )
    print(
        f"Warm-up         : {warmup_days} days"
    )

    print()
    print(
        "[1/5] Downloading M5 historical data..."
    )

    candles = fetch_m5_candles(
        download_start,
        end_timestamp,
    )

    if not candles:
        raise RuntimeError(
            "No BTCUSD candles downloaded."
        )

    print(
        f"[OK] M5 candles: {len(candles)}"
    )

    print()
    print(
        "[2/5] Preparing MTF market data..."
    )

    market = prepare_market(
        candles
    )

    print(
        f"[OK] M15 candles: {len(market.m15)}"
    )
    print(
        f"[OK] H1 candles : {len(market.h1)}"
    )
    print(
        f"[OK] H4 candles : {len(market.h4)}"
    )
    print(
        f"[OK] D1 candles : {len(market.d1)}"
    )

    news_events: List[NewsEvent] = []

    print()

    if args.news_file:
        print(
            "[3/5] Loading historical news..."
        )

        news_events = load_news_file(
            args.news_file
        )

        print(
            f"[OK] News events: "
            f"{len(news_events)}"
        )

    else:
        print(
            "[3/5] No historical news supplied."
        )
        print(
            "[WARNING] C_MTF_NEWS will not have "
            "historical news validation."
        )

    print()
    print(
        "[4/5] Running walk-forward..."
    )

    oos_start = requested_start
    oos_end = end_timestamp

    results = run_walk_forward(
        market=market,
        events=news_events,
        start_timestamp=oos_start,
        end_timestamp=oos_end,
        train_days=args.walk_forward_train,
        test_days=args.walk_forward_test,
    )

    print()
    print(
        "========================================="
    )
    print(
        " FINAL OUT-OF-SAMPLE RESULTS"
    )
    print(
        "========================================="
    )

    combined_trades: List[TradeRecord] = []

    for strategy in SUPPORTED_STRATEGIES:
        report = performance(
            strategy,
            results[strategy],
        )

        print_performance(report)

        combined_trades.extend(
            results[strategy]
        )

    print()
    print(
        "[5/5] Saving OOS trade database..."
    )

    save_trades(
        args.output,
        combined_trades,
    )

    print(
        f"[OK] Saved: {args.output}"
    )

    if not args.news_file:
        print()
        print(
            "[IMPORTANT]"
        )
        print(
            "This run validates technical/MTF logic."
        )
        print(
            "It does NOT validate the news filter."
        )


if __name__ == "__main__":
    main()
