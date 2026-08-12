#!/usr/bin/env python3
"""
gti_v2_unified_daemon.py

GTI-AI V2 unified daemon.

Responsibilities:
- Run the M5 downloader.
- Classify downloader results as FRESH, STALE, or ERROR.
- Run the strategy only after fresh data.
- Maintain the signal state machine independently from the validator.
- Persist signal state across process restarts.
- Apply exponential backoff after downloader errors.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


DOWNLOADER_SCRIPT = "gti_v2_1_3_1_downloader.py"
STRATEGY_SCRIPT = "gti_v2_wfo.py"
STATE_FILE = Path("gti_signal_state.json")

INITIAL_BACKOFF = 10
MAX_BACKOFF = 300
STALE_SLEEP = 5
FRESH_SLEEP = 15
SUBPROCESS_TIMEOUT = 30


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
    """Validated strategy signal consumed by the state machine."""

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
        self.last_signal_direction: Direction | None = None
        self.last_entry_price = 0.0
        self.last_stop_price = 0.0
        self.last_target_price = 0.0
        self.last_signal_timestamp = 0.0
        self.load()

    @property
    def last_signal_direction_value(self) -> str | None:
        """Return the persisted direction value."""

        if self.last_signal_direction is None:
            return None
        return (self.last_signal_direction.value if hasattr(self.last_signal_direction, 'value') else self.last_signal_direction) if self.last_signal_direction else None

    def save(self) -> None:
        """Persist the state-machine state."""

        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "state": self.state.value,
            "last_signal_direction": (
                (self.last_signal_direction.value if hasattr(self.last_signal_direction, 'value') else self.last_signal_direction) if self.last_signal_direction else None
                if self.last_signal_direction is not None
                else None
            ),
            "last_entry_price": self.last_entry_price,
            "last_stop_price": self.last_stop_price,
            "last_target_price": self.last_target_price,
            "last_signal_timestamp": self.last_signal_timestamp,
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

            self.state = SignalState(
                data.get("state", SignalState.WAIT.value)
            )

            direction = data.get("last_signal_direction")

            if direction is None:
                self.last_signal_direction = None
            else:
                self.last_signal_direction = Direction(direction)

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

        except (OSError, ValueError, TypeError, json.JSONDecodeError):
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

        self.state = SignalState.ALERT_SENT
        self.last_signal_direction = Direction(signal.direction.upper()) if isinstance(signal.direction, str) else signal.direction
        self.last_entry_price = signal.entry
        self.last_stop_price = signal.stop
        self.last_target_price = signal.target
        self.last_signal_timestamp = signal.candle_timestamp
        self.save()

    def transition_invalidated(self, reason: str) -> None:
        """Move the current setup into INVALIDATED."""

        self.state = SignalState.INVALIDATED
        self.save()

    def transition_wait(self, reason: str) -> None:
        """Reset the state machine to WAIT."""

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

        if self.last_signal_direction != signal.direction:
            return True, "Direction changed"

        if self.last_entry_price <= 0:
            return True, "Missing previous entry"

        entry_delta = abs(
            signal.entry - self.last_entry_price
        ) / self.last_entry_price

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


def poll_market_data() -> str:
    """Run the downloader and classify its result."""

    script = Path(DOWNLOADER_SCRIPT)

    if not script.exists():
        print(
            f"[DAEMON ERROR] Downloader not found: {script}"
        )
        return "ERROR"

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("[DAEMON ERROR] Downloader timed out.")
        return "ERROR"
    except OSError as exc:
        print(
            f"[DAEMON ERROR] Failed to execute downloader: {exc}"
        )
        return "ERROR"

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)

    if result.returncode == 0:
        print("[DAEMON] FRESH DATA: New M5 candle detected.")
        return "FRESH"

    if result.returncode == 2:
        print("[DAEMON] STALE DATA: No new M5 candle.")
        return "STALE"

    print(
        "[DAEMON ERROR] Downloader exited with "
        f"code {result.returncode}."
    )
    return "ERROR"


def run_strategy_evaluation() -> int:
    """Run the strategy after fresh market data."""

    script = Path(STRATEGY_SCRIPT)

    if not script.exists():
        print(
            f"[DAEMON ERROR] Strategy script not found: {script}"
        )
        return 1

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("[DAEMON ERROR] Strategy timed out.")
        return 1
    except OSError as exc:
        print(
            f"[DAEMON ERROR] Failed to execute strategy: {exc}"
        )
        return 1

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)

    return result.returncode


def main_loop() -> None:
    """Run the daemon until interrupted."""

    error_backoff = INITIAL_BACKOFF

    while True:
        status = poll_market_data()

        if status == "FRESH":
            error_backoff = INITIAL_BACKOFF
            run_strategy_evaluation()
            time.sleep(FRESH_SLEEP)

        elif status == "STALE":
            time.sleep(STALE_SLEEP)

        else:
            print(
                "[DAEMON] Error received. "
                f"Backing off for {error_backoff} seconds..."
            )
            time.sleep(error_backoff)
            error_backoff = min(
                error_backoff * 2,
                MAX_BACKOFF,
            )


def main() -> None:
    """Run the daemon until interrupted."""

    print("[DAEMON] GTI-AI V2 Unified Daemon starting...")

    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n[DAEMON] Stopped gracefully by user.")
        raise SystemExit(0)


if __name__ == "__main__":
    main()
