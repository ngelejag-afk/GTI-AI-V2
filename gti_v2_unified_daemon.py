#!/usr/bin/env python3
"""
gti_v2_unified_daemon.py

GTI-AI V2 live unified daemon.

The daemon reuses the existing validator implementation instead of
depending on the nonexistent gti_v2_1_3_1_downloader.py script.

Responsibilities:
- Maintain a local M5 candle cache.
- Fetch only a large warm-up history on first startup.
- Incrementally refresh recent M5 candles.
- Ignore incomplete M5 candles.
- Reuse the validator's MTF and EMA crossover logic.
- Support A_TECH_ONLY, B_MTF_ONLY and C_MTF_NEWS.
- Calculate ATR-based entry, stop and 2R target using validator rules.
- Persist signal state across restarts.
- Apply exponential backoff after data/API errors.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

from models.news_event import NewsEvent
from news.news_service import NewsService

from gti_v2_1_2_validator import (
    ATR_PERIOD,
    M15_SECONDS,
    M5_SECONDS,
    SL_ATR_MULTIPLIER,
    TP_R_MULTIPLE,
    SUPPORTED_STRATEGIES,
    Candle,
    PreparedMarket,
    Signal,
    apply_news_to_signal,
    fetch_m5_candles,
    get_m15_signal,
    prepare_market,
    strategy_allows_signal,
)


BASE_DIR = Path(__file__).resolve().parent

STATE_FILE = BASE_DIR / "gti_signal_state.json"
CANDLE_CACHE_FILE = BASE_DIR / "gti_m5_cache.json"

DEFAULT_STRATEGY = "A_TECH_ONLY"

INITIAL_BACKOFF = 10
MAX_BACKOFF = 300

DEFAULT_NTFY_TOPIC_URL = "https://ntfy.sh/gti_ai_geoffrey_signals"
NTFY_TIMEOUT_SECONDS = 10

FRESH_SLEEP = 15
STALE_SLEEP = 60

SUBPROCESS_TIMEOUT = 30

INITIAL_HISTORY_DAYS = 60
INCREMENTAL_LOOKBACK_SECONDS = 2 * 60 * 60

CACHE_MAX_DAYS = 90


class NtfyNotifier:
    """Send GTI-AI notifications through ntfy.sh."""

    def __init__(
        self,
        topic_url: str | None = None,
        timeout: float = NTFY_TIMEOUT_SECONDS,
    ) -> None:
        configured_url = topic_url or os.getenv(
            "NTFY_TOPIC_URL",
            DEFAULT_NTFY_TOPIC_URL,
        )
        self.topic_url = configured_url.rstrip("/")
        self.timeout = timeout

    def send(
        self,
        title: str,
        message: str,
        priority: str = "high",
        tags: str = "chart_with_upwards_trend",
    ) -> bool:
        """Publish one notification and return whether it succeeded."""

        request = urllib.request.Request(
            self.topic_url,
            data=message.encode("utf-8"),
            method="POST",
            headers={
                "Title": title,
                "Priority": priority,
                "Tags": tags,
                "Content-Type": "text/plain; charset=utf-8",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                return 200 <= response.status < 300
        except (
            OSError,
            urllib.error.HTTPError,
            urllib.error.URLError,
        ) as exc:
            print(
                f"[NTFY ERROR] {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            return False


class Direction(str, Enum):
    """Trading direction."""

    BUY = "BUY"
    SELL = "SELL"


class SignalState(str, Enum):
    """Persistent signal lifecycle state."""

    WAIT = "WAIT"
    ALERT_SENT = "ALERT_SENT"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class Indicators:
    """Indicator snapshot attached to a strategy signal."""

    ema_fast: float
    ema_slow: float
    rsi: float
    atr: float
    volume_sma: float


@dataclass(frozen=True)
class StrategySignal:
    """Signal representation consumed by the daemon state machine."""

    direction: Direction
    entry: float
    stop: float
    target: float
    risk_reward: float
    score: float
    valid: bool
    reason: str
    candle_timestamp: float
    indicators: Indicators


class SignalStateMachine:
    """Persist and evaluate signal state transitions."""

    MATERIAL_ENTRY_CHANGE_PCT = 0.004

    def __init__(self, filepath: Path = STATE_FILE) -> None:
        self.filepath = Path(filepath)
        self.state = SignalState.WAIT
        self.last_signal_direction: Optional[Direction] = None
        self.last_entry_price = 0.0
        self.last_stop_price = 0.0
        self.last_target_price = 0.0
        self.last_signal_timestamp = 0.0
        self.last_processed_m15_timestamp = 0
        self.load()

    @staticmethod
    def _normalize_direction(direction: Direction | str) -> Direction:
        """Normalize a signal direction to the internal enum."""

        if isinstance(direction, Direction):
            return direction

        try:
            return Direction(str(direction).strip().upper())
        except ValueError as exc:
            raise ValueError(
                f"Unsupported signal direction: {direction!r}"
            ) from exc

    @property
    def last_signal_direction_value(self) -> Optional[str]:
        """Return the persisted direction value."""

        if self.last_signal_direction is None:
            return None

        return self._normalize_direction(
            self.last_signal_direction
        ).value

    def save(self) -> None:
        """Persist the state machine state."""

        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "state": self.state.value,
            "last_signal_direction": self.last_signal_direction_value,
            "last_entry_price": self.last_entry_price,
            "last_stop_price": self.last_stop_price,
            "last_target_price": self.last_target_price,
            "last_signal_timestamp": self.last_signal_timestamp,
            "last_processed_m15_timestamp": self.last_processed_m15_timestamp,
        }

        self.filepath.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def load(self) -> None:
        """Restore state from disk when available."""

        if not self.filepath.exists():
            return

        try:
            data = json.loads(
                self.filepath.read_text(encoding="utf-8")
            )

            state_value = data.get(
                "state",
                SignalState.WAIT.value,
            )

            self.state = SignalState(state_value)

            direction = data.get("last_signal_direction")

            if direction is None:
                self.last_signal_direction = None
            else:
                self.last_signal_direction = Direction(
                    str(direction).upper()
                )

            self.last_entry_price = float(
                data.get("last_entry_price", 0.0)
            )

            self.last_stop_price = float(
                data.get("last_stop_price", 0.0)
            )

            self.last_target_price = float(
                data.get("last_target_price", 0.0)
            )

            self.last_signal_timestamp = float(
                data.get("last_signal_timestamp", 0.0)
            )

            self.last_processed_m15_timestamp = int(
                data.get("last_processed_m15_timestamp", 0)
            )

        except (
            OSError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ):
            self._reset()

    def _reset(self) -> None:
        """Reset corrupted or unreadable persisted state."""

        self.state = SignalState.WAIT
        self.last_signal_direction = None
        self.last_entry_price = 0.0
        self.last_stop_price = 0.0
        self.last_target_price = 0.0
        self.last_signal_timestamp = 0.0

    def transition_alert(self, signal: StrategySignal) -> None:
        """Move a valid signal into ALERT_SENT."""

        if not signal.valid:
            raise ValueError(
                "Cannot transition an invalid signal into ALERT_SENT."
            )

        direction = self._normalize_direction(signal.direction)

        self.state = SignalState.ALERT_SENT
        self.last_signal_direction = direction
        self.last_entry_price = signal.entry
        self.last_stop_price = signal.stop
        self.last_target_price = signal.target
        self.last_signal_timestamp = signal.candle_timestamp
        self.save()

    def transition_invalidated(self, reason: str) -> None:
        """Move the current setup into INVALIDATED."""

        del reason

        self.state = SignalState.INVALIDATED
        self.save()

    def transition_wait(self, reason: str) -> None:
        """Reset the state machine to WAIT."""

        del reason

        self.state = SignalState.WAIT
        self.save()

    def should_alert(
        self,
        signal: StrategySignal,
    ) -> tuple[bool, str]:
        """Determine whether a signal represents a new alert."""

        if not signal.valid:
            return False, "Setup invalid"

        if self.state == SignalState.WAIT:
            return True, "Fresh setup"

        if self.state == SignalState.INVALIDATED:
            return True, "Setup recovered"

        signal_direction = self._normalize_direction(
            signal.direction
        )

        if self.last_signal_direction != signal_direction:
            return True, "Direction changed"

        if self.last_entry_price <= 0:
            return True, "Missing previous entry"

        entry_delta = (
            abs(signal.entry - self.last_entry_price)
            / self.last_entry_price
        )

        if entry_delta > self.MATERIAL_ENTRY_CHANGE_PCT:
            return True, "Material entry change"

        return False, "Duplicate signal"

    def evaluate(
        self,
        signal: StrategySignal,
    ) -> tuple[SignalState, bool, str]:
        """Evaluate and apply a strategy signal."""

        should_alert, reason = self.should_alert(signal)

        if not signal.valid:
            self.transition_invalidated(signal.reason)
            return self.state, False, "Setup invalid"

        if should_alert:
            self.transition_alert(signal)
            return self.state, True, reason

        return self.state, False, reason


def parse_args() -> argparse.Namespace:
    """Parse daemon command-line arguments."""

    parser = argparse.ArgumentParser(
        description="GTI-AI V2 unified live daemon."
    )

    parser.add_argument(
        "--strategy",
        choices=SUPPORTED_STRATEGIES,
        default=DEFAULT_STRATEGY,
        help="Live strategy to evaluate.",
    )

    parser.add_argument(
        "--state-file",
        type=Path,
        default=STATE_FILE,
        help="Persistent signal state file.",
    )

    parser.add_argument(
        "--cache-file",
        type=Path,
        default=CANDLE_CACHE_FILE,
        help="Persistent M5 candle cache.",
    )

    parser.add_argument(
        "--initial-history-days",
        type=int,
        default=INITIAL_HISTORY_DAYS,
        help="Initial historical M5 warm-up period.",
    )

    parser.add_argument(
        "--news-file",
        type=Path,
        default=None,
        help="Economic news JSON/CSV file.",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Perform one evaluation cycle and exit.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print additional daemon diagnostics.",
    )

    return parser.parse_args()


def load_candle_cache(filepath: Path) -> list[Candle]:
    """Load cached candles from disk."""

    if not filepath.exists():
        return []

    try:
        payload = json.loads(
            filepath.read_text(encoding="utf-8")
        )

        if not isinstance(payload, list):
            return []

        candles: dict[int, Candle] = {}

        for item in payload:
            if not isinstance(item, dict):
                continue

            try:
                candle = Candle(
                    timestamp=int(item["timestamp"]),
                    open=float(item["open"]),
                    high=float(item["high"]),
                    low=float(item["low"]),
                    close=float(item["close"]),
                    volume=float(item["volume"]),
                )
            except (KeyError, TypeError, ValueError):
                continue

            candles[candle.timestamp] = candle

        return sorted(
            candles.values(),
            key=lambda candle: candle.timestamp,
        )

    except (
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ):
        return []


def save_candle_cache(
    filepath: Path,
    candles: Sequence[Candle],
) -> None:
    """Persist candles to disk."""

    filepath.parent.mkdir(parents=True, exist_ok=True)

    payload = [
        {
            "timestamp": candle.timestamp,
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
        }
        for candle in candles
    ]

    filepath.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )


def trim_candle_cache(
    candles: Sequence[Candle],
    now_timestamp: int,
) -> list[Candle]:
    """Keep only the configured rolling cache window."""

    cutoff = now_timestamp - CACHE_MAX_DAYS * 86400

    return [
        candle
        for candle in candles
        if candle.timestamp >= cutoff
    ]


def merge_candles(
    existing: Sequence[Candle],
    incoming: Sequence[Candle],
    now_timestamp: int,
) -> list[Candle]:
    """Merge, deduplicate and trim candle data."""

    candles: dict[int, Candle] = {
        candle.timestamp: candle
        for candle in existing
    }

    for candle in incoming:
        candles[candle.timestamp] = candle

    merged = sorted(
        candles.values(),
        key=lambda candle: candle.timestamp,
    )

    return trim_candle_cache(
        merged,
        now_timestamp,
    )


def filter_completed_m5(
    candles: Sequence[Candle],
    now_timestamp: int,
) -> list[Candle]:
    """Return only completed M5 candles."""

    return [
        candle
        for candle in candles
        if candle.timestamp + M5_SECONDS <= now_timestamp
    ]


def fetch_market_candles(
    filepath: Path,
    initial_history_days: int,
    verbose: bool,
) -> tuple[list[Candle], bool]:
    """Load cache and incrementally refresh market data."""

    now_timestamp = int(time.time())
    cached = load_candle_cache(filepath)

    if cached:
        start_timestamp = max(
            cached[-1].timestamp - M5_SECONDS,
            now_timestamp - INCREMENTAL_LOOKBACK_SECONDS,
        )

        mode = "incremental"
    else:
        start_timestamp = (
            now_timestamp
            - initial_history_days * 86400
        )

        mode = "initial"

    if verbose:
        print(
            f"[DAEMON] Data refresh: {mode}; "
            f"cached candles={len(cached)}"
        )

    downloaded = fetch_m5_candles(
        start_timestamp,
        now_timestamp,
    )

    merged = merge_candles(
        cached,
        downloaded,
        now_timestamp,
    )

    save_candle_cache(filepath, merged)

    completed = filter_completed_m5(
        merged,
        now_timestamp,
    )

    if not completed:
        raise RuntimeError(
            "No completed M5 candles are available."
        )

    return completed, bool(downloaded)


def find_latest_completed_m15_index(
    market: PreparedMarket,
    now_timestamp: int,
) -> Optional[int]:
    """Find the newest M15 candle that is fully completed."""

    latest_index: Optional[int] = None

    for index, candle in enumerate(market.m15):
        if candle.timestamp + M15_SECONDS <= now_timestamp:
            latest_index = index
        else:
            break

    return latest_index


def get_latest_signal(
    market: PreparedMarket,
    now_timestamp: int,
    strategy: str,
    events: Sequence[NewsEvent],
) -> tuple[Optional[Signal], Optional[int]]:
    """Evaluate the newest completed M15 candle."""

    m15_index = find_latest_completed_m15_index(
        market,
        now_timestamp,
    )

    if m15_index is None:
        return None, None

    signal = get_m15_signal(
        market,
        m15_index,
    )

    if signal is None:
        return None, m15_index

    signal = apply_news_to_signal(
        signal,
        events,
    )

    if not strategy_allows_signal(
        signal,
        strategy,
    ):
        return None, m15_index

    return signal, m15_index


def build_strategy_signal(
    market: PreparedMarket,
    signal: Signal,
    m15_index: int,
) -> StrategySignal:
    """Convert a validator signal into the daemon signal model."""

    atr = market.m15_atr[m15_index]

    if atr is None or atr <= 0:
        raise ValueError(
            "ATR is unavailable for the current M15 signal."
        )

    entry_index = None

    for index, candle in enumerate(market.m5):
        if candle.timestamp >= signal.timestamp:
            entry_index = index
            break

    if entry_index is None:
        raise ValueError(
            "No M5 entry candle exists after the signal timestamp."
        )

    entry = market.m5[entry_index].open

    sl_distance = atr * SL_ATR_MULTIPLIER

    if signal.direction == "BUY":
        stop = entry - sl_distance
        target = entry + sl_distance * TP_R_MULTIPLE
    else:
        stop = entry + sl_distance
        target = entry - sl_distance * TP_R_MULTIPLE

    if sl_distance <= 0:
        raise ValueError("Invalid stop distance.")

    risk_reward = abs(target - entry) / sl_distance

    m15_state = market.m15_states[m15_index]

    ema_fast = (
        m15_state.ema20
        if m15_state.ema20 is not None
        else 0.0
    )

    ema_slow = (
        m15_state.ema50
        if m15_state.ema50 is not None
        else 0.0
    )

    volume_sma = 0.0

    if entry_index >= 20:
        recent_volume = [
            candle.volume
            for candle in market.m5[
                entry_index - 20 : entry_index
            ]
        ]

        if recent_volume:
            volume_sma = sum(recent_volume) / len(recent_volume)

    return StrategySignal(
        direction=Direction(signal.direction),
        entry=entry,
        stop=stop,
        target=target,
        risk_reward=risk_reward,
        score=float(signal.score),
        valid=True,
        reason=(
            f"{signal.direction} EMA20/EMA50 crossover; "
            f"MTF={signal.mtf.alignment_score}; "
            f"news={signal.news.score}"
        ),
        candle_timestamp=float(signal.timestamp),
        indicators=Indicators(
            ema_fast=ema_fast,
            ema_slow=ema_slow,
            rsi=0.0,
            atr=atr,
            volume_sma=volume_sma,
        ),
    )


def format_signal_notification(
    signal: StrategySignal,
    reason: str,
    strategy: str,
) -> str:
    """Build the manual MT5 execution notification."""

    return (
        "EXECUTION ACTIVE\n"
        "MANUAL MT5 EXECUTION\n"
        "====================\n"
        f"Strategy : {strategy}\n"
        f"Direction: {signal.direction.value}\n"
        f"Entry    : {signal.entry:.2f}\n"
        f"SL       : {signal.stop:.2f}\n"
        f"TP       : {signal.target:.2f}\n"
        f"R:R      : {signal.risk_reward:.2f}R\n"
        f"Score    : {signal.score:.0f}\n"
        f"ATR      : {signal.indicators.atr:.2f}\n"
        f"Reason   : {reason}\n"
        "====================\n"
        "ENTER MANUALLY IN MT5\n"
        "AUTO EXECUTION: OFF"
    )


def print_signal(
    signal: StrategySignal,
    reason: str,
    strategy: str,
) -> None:
    """Print a newly accepted signal."""

    print()
    print("========================================")
    print("[DAEMON] NEW SIGNAL")
    print("========================================")
    print(f"Strategy   : {strategy}")
    print(f"Direction  : {signal.direction.value}")
    print(f"Entry      : {signal.entry:.2f}")
    print(f"Stop       : {signal.stop:.2f}")
    print(f"Target     : {signal.target:.2f}")
    print(f"Risk/Reward: {signal.risk_reward:.2f}R")
    print(f"Score      : {signal.score:.0f}")
    print(f"ATR        : {signal.indicators.atr:.2f}")
    print(f"Reason     : {reason}")
    print("========================================")
    print()


def evaluate_once(
    state_machine: SignalStateMachine,
    strategy: str,
    cache_file: Path,
    initial_history_days: int,
    verbose: bool,
    notifier: NtfyNotifier | None = None,
    news_file: Path | None = None,
) -> str:
    """Run one complete live evaluation cycle."""

    now_timestamp = int(time.time())

    candles, downloaded = fetch_market_candles(
        cache_file,
        initial_history_days,
        verbose,
    )

    if verbose:
        latest_timestamp = candles[-1].timestamp

        print(
            f"[DAEMON] Completed M5 candles: {len(candles)}"
        )
        print(
            f"[DAEMON] Latest M5 timestamp: {latest_timestamp}"
        )

    if not downloaded:
        return "STALE"

    market = prepare_market(candles)

    m15_index = find_latest_completed_m15_index(
        market,
        now_timestamp,
    )

    if m15_index is None:
        print("[DAEMON] No completed M15 candle available.")
        return "STALE"

    current_m15_timestamp = market.m15[m15_index].timestamp

    if current_m15_timestamp <= state_machine.last_processed_m15_timestamp:
        if verbose:
            print(
                "[DAEMON] M15 candle unchanged; "
                f"already processed timestamp={current_m15_timestamp}"
            )
        return "STALE"

    state_machine.last_processed_m15_timestamp = current_m15_timestamp
    state_machine.save()

    events: list[NewsEvent] = []

    if news_file is not None:
        events = NewsService.load_file(news_file)

        if verbose:
            print(
                f"[DAEMON] News events loaded: "
                f"{len(events)} from {news_file}"
            )

    signal, evaluated_m15_index = get_latest_signal(
        market=market,
        now_timestamp=now_timestamp,
        strategy=strategy,
        events=events,
    )

    if evaluated_m15_index != m15_index:
        raise RuntimeError(
            "Latest M15 index changed during signal evaluation."
        )

    if signal is None:
        print(
            "[DAEMON] No qualifying signal "
            "on latest completed M15 candle."
        )
        return "FRESH"

    strategy_signal = build_strategy_signal(
        market,
        signal,
        m15_index,
    )

    state, alert, reason = state_machine.evaluate(
        strategy_signal,
    )

    print(
        f"[DAEMON] {strategy} {signal.direction} "
        f"state={state.value} alert={alert} reason={reason}"
    )

    if alert:
        print_signal(
            strategy_signal,
            reason,
            strategy,
        )

        if notifier is not None:
            notification = format_signal_notification(
                strategy_signal,
                reason,
                strategy,
            )
            sent = notifier.send(
                title="GTI-AI EXECUTION ACTIVE",
                message=notification,
                priority="high",
                tags="moneybag,chart_with_upwards_trend",
            )
            print(f"[NTFY] Signal notification sent={sent}")

    return "FRESH"


def main_loop(
    state_machine: SignalStateMachine,
    strategy: str,
    cache_file: Path,
    initial_history_days: int,
    verbose: bool,
    notifier: NtfyNotifier | None = None,
    news_file: Path | None = None,
) -> None:
    """Run the daemon continuously."""

    m15_interval_seconds = 15 * 60
    m15_grace_seconds = 5
    error_backoff = INITIAL_BACKOFF

    while True:
        try:
            evaluate_once(
                state_machine=state_machine,
                strategy=strategy,
                cache_file=cache_file,
                initial_history_days=initial_history_days,
                verbose=verbose,
                notifier=notifier,
                news_file=news_file,
            )

            error_backoff = INITIAL_BACKOFF

            now = time.time()
            next_boundary = (
                (int(now) // m15_interval_seconds + 1)
                * m15_interval_seconds
            )
            sleep_seconds = (
                next_boundary
                + m15_grace_seconds
                - now
            )

            if sleep_seconds < 1:
                sleep_seconds = 1

            if verbose:
                print(
                    "[DAEMON] Next M15 evaluation in "
                    f"{sleep_seconds:.1f} seconds."
                )

            time.sleep(sleep_seconds)

        except KeyboardInterrupt:
            raise

        except Exception as exc:
            print(
                f"[DAEMON ERROR] {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )

            print(
                "[DAEMON] Error received. "
                f"Backing off for {error_backoff} seconds..."
            )

            time.sleep(error_backoff)

            error_backoff = min(
                error_backoff * 2,
                MAX_BACKOFF,
            )

def main() -> int:
    """Run the GTI-AI V2 unified daemon."""

    args = parse_args()

    if args.initial_history_days <= 0:
        print(
            "[DAEMON ERROR] "
            "--initial-history-days must be greater than zero.",
            file=sys.stderr,
        )
        return 2

    state_machine = SignalStateMachine(
        args.state_file,
    )

    notifier = NtfyNotifier()

    print("[DAEMON] GTI-AI V2 Unified Daemon starting...")
    print(f"[DAEMON] Strategy : {args.strategy}")
    print(f"[DAEMON] State    : {args.state_file}")
    print(f"[DAEMON] Cache    : {args.cache_file}")
    print(f"[DAEMON] News     : {args.news_file or '<disabled>'}")
    print(f"[DAEMON] Initial state: {state_machine.state.value}")
    print(f"[DAEMON] ntfy     : {notifier.topic_url}")

    if args.news_file is not None and not args.news_file.exists():
        print(
            f"[DAEMON ERROR] News file does not exist: "
            f"{args.news_file}",
            file=sys.stderr,
        )
        return 2

    if args.once:
        try:
            evaluate_once(
                state_machine=state_machine,
                strategy=args.strategy,
                cache_file=args.cache_file,
                initial_history_days=args.initial_history_days,
                verbose=args.verbose,
                notifier=notifier,
                news_file=args.news_file,
            )
        except KeyboardInterrupt:
            print("\n[DAEMON] Stopped gracefully by user.")
            return 0
        except Exception as exc:
            print(
                f"[DAEMON ERROR] {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            return 1

        return 0

    try:
        main_loop(
            state_machine=state_machine,
            strategy=args.strategy,
            cache_file=args.cache_file,
            initial_history_days=args.initial_history_days,
            verbose=args.verbose,
            notifier=notifier,
            news_file=args.news_file,
        )
    except KeyboardInterrupt:
        print("\n[DAEMON] Stopped gracefully by user.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
