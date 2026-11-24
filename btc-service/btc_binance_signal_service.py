"""
GTI BTCUSD Binance Signal Service
==================================
Standalone service — fetches BTCUSDT candles directly from the Binance
public data API, runs a lightweight SMC/ICT-style analysis (BOS, CHoCH,
Order Blocks, FVG, liquidity sweeps), and pushes signals straight to ntfy.sh.

Runs entirely on Render. No Termux, no MT5, no external dependency —
pure Python standard library only.

Reliability V2 candidate: serialized Binance/ntfy outbound requests.

v3: retries failed ntfy.sh deliveries (up to 3 attempts) and always
records the outcome of a closed trade in /health as "last_closed_trade",
so the outcome is visible even if the push notification itself never
reached the phone.
"""

import os
import json
import copy
import time
import threading
import urllib.request
import urllib.error
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# Config (override any of these via Render environment variables)
# ---------------------------------------------------------------------------
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))

BINANCE_SYMBOL = os.environ.get("BINANCE_SYMBOL", "BTCUSDT")
BINANCE_INTERVAL = os.environ.get("BINANCE_INTERVAL", "5m")
BINANCE_KLINES_URL = "https://data-api.binance.vision/api/v3/klines"
CANDLE_LIMIT = 150

NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()
NTFY_MAX_RETRIES = max(1, int(os.environ.get("NTFY_MAX_RETRIES", "3")))
NTFY_RETRY_DELAY_SECONDS = max(1, int(os.environ.get("NTFY_RETRY_DELAY_SECONDS", "5")))
NTFY_MAX_BACKOFF_SECONDS = 30
# Serialize cooldown check + notification HTTP attempts across scanner/heartbeat.
NTFY_SEND_LOCK = threading.Lock()

# Independent monitoring heartbeat; 900 seconds = 15 minutes.
NTFY_HEARTBEAT_INTERVAL_SECONDS = max(
    0, int(os.environ.get("NTFY_HEARTBEAT_INTERVAL_SECONDS", "900"))
)
BINANCE_TICKER_PRICE_URL = "https://data-api.binance.vision/api/v3/ticker/price"

# Scan the market every 1 minute for tighter, more responsive entries.
SCAN_INTERVAL_SECONDS = int(os.environ.get("SCAN_INTERVAL_SECONDS", "60"))

# New-entry (BUY/SELL) notifications are throttled to at most one every
# 30 minutes, to avoid spamming while scanning every 1 minute.
MIN_SIGNAL_NOTIFY_INTERVAL_SECONDS = int(
    os.environ.get("MIN_SIGNAL_NOTIFY_INTERVAL_SECONDS", "1800")
)

SWING_LOOKBACK = 3   # candles each side required to confirm a swing high/low
MIN_RR = 2.0         # minimum reward:risk enforced on generated trade levels


# ---------------------------------------------------------------------------
# Shared state (read by the HTTP server, written by the scan loop)
# ---------------------------------------------------------------------------
class State:
    lock = threading.Lock()
    ntfy_lock = threading.RLock()
    ntfy_blocked_until = 0.0
    ntfy_consecutive_429 = 0
    last_signal = {
        "symbol": BINANCE_SYMBOL.replace("USDT", "USD"),
        "decision": "WAIT",
        "direction": "WAIT",
        "confidence": 0.0,
        "market_bias": "Unknown",
        "entry": 0.0,
        "stop_loss": 0.0,
        "take_profit": 0.0,
        "confluences": [],
        "updated": "--:--:-- UTC",
    }
    last_error = None

    # The currently "open" trade this service is tracking (from the last
    # BUY/SELL notification it sent). None if no trade is being tracked.
    active_trade = None

    # Record of how the most recent trade ended, so the outcome is
    # visible via /health even if the push notification itself failed
    # to reach the phone.
    last_closed_trade = None

    # Separate successful notification and retry timestamps.
    last_signal_notify_ts = 0.0
    last_signal_attempt_ts = 0.0

    ntfy_delivery = {
        "successes": 0,
        "failures": 0,
        "rate_limited": 0,
        "deferred": 0,
        "cooldown_seconds": 0,
        "last_status": "never",
        "last_http_status": None,
        "last_error": None,
        "last_attempts": 0,
        "last_attempt_at": None,
        "last_success_at": None,
    }
    last_entry_notification = None


# ---------------------------------------------------------------------------
# Binance market data and shared rate-limit protection
# ---------------------------------------------------------------------------
BINANCE_LOCK = threading.Lock()
# Serialize cooldown check + outbound request so concurrent callers cannot
# pass the same preflight check and hit Binance together. This lock is never
# used for metrics/state snapshots.
BINANCE_REQUEST_LOCK = threading.Lock()
BINANCE_BLOCKED_UNTIL = 0.0
BINANCE_CONSECUTIVE_LIMITS = 0
BINANCE_LAST_HTTP_STATUS = None
BINANCE_LAST_ERROR = None
BINANCE_RATE_LIMIT_EVENTS = 0
BINANCE_FALLBACK_418_SECONDS = 900
BINANCE_FALLBACK_429_SECONDS = 60
BINANCE_MAX_FALLBACK_SECONDS = 3600


class BinanceCooldownError(RuntimeError):
    """Raised locally while Binance has instructed this service to back off."""


def binance_cooldown_remaining():
    with BINANCE_LOCK:
        return max(0.0, BINANCE_BLOCKED_UNTIL - time.monotonic())


def _binance_urlopen_serialized(request, timeout):
    global BINANCE_BLOCKED_UNTIL, BINANCE_CONSECUTIVE_LIMITS
    global BINANCE_LAST_HTTP_STATUS, BINANCE_LAST_ERROR, BINANCE_RATE_LIMIT_EVENTS
    remaining = binance_cooldown_remaining()
    if remaining > 0:
        raise BinanceCooldownError(f"Binance cooldown active for {remaining:.0f}s; request suppressed")
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if exc.code in (418, 429):
            retry_after = _retry_after_seconds((exc.headers or {}).get("Retry-After"))
            with BINANCE_LOCK:
                BINANCE_CONSECUTIVE_LIMITS += 1
                base = BINANCE_FALLBACK_418_SECONDS if exc.code == 418 else BINANCE_FALLBACK_429_SECONDS
                fallback = min(base * (2 ** (BINANCE_CONSECUTIVE_LIMITS - 1)), BINANCE_MAX_FALLBACK_SECONDS)
                delay = retry_after if retry_after is not None else fallback
                BINANCE_BLOCKED_UNTIL = max(BINANCE_BLOCKED_UNTIL, time.monotonic() + delay)
                BINANCE_LAST_HTTP_STATUS = exc.code
                BINANCE_LAST_ERROR = str(exc)
                BINANCE_RATE_LIMIT_EVENTS += 1
            print(f"[BINANCE HTTP {exc.code}] Shared cooldown={delay:.0f}s", flush=True)
        raise
    else:
        with BINANCE_LOCK:
            BINANCE_CONSECUTIVE_LIMITS = 0
            BINANCE_LAST_HTTP_STATUS = getattr(response, "status", 200)
            BINANCE_LAST_ERROR = None
        return response


def _binance_urlopen(request, timeout):
    # Keep the request lock from cooldown check through HTTP response headers.
    # The metrics lock remains short-lived and is not held during network I/O.
    with BINANCE_REQUEST_LOCK:
        return _binance_urlopen_serialized(request, timeout)


def fetch_klines(symbol=BINANCE_SYMBOL, interval=BINANCE_INTERVAL, limit=CANDLE_LIMIT):
    url = f"{BINANCE_KLINES_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "gti-ai-render/1.0"})

    with _binance_urlopen(req, timeout=15) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    candles = []
    for row in raw:
        candles.append({
            "open_time": row[0],
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "volume": float(row[5]),
            "close_time": row[6],
        })
    return candles


# ---------------------------------------------------------------------------
# Structure: swing points, BOS, CHoCH
# ---------------------------------------------------------------------------
def find_swing_points(candles, lookback=SWING_LOOKBACK):
    """Return confirmed swing highs/lows as (index, price) tuples."""
    highs, lows = [], []
    n = len(candles)

    for i in range(lookback, n - lookback):
        window = candles[i - lookback:i + lookback + 1]
        h, l = candles[i]["high"], candles[i]["low"]

        if h == max(c["high"] for c in window):
            highs.append((i, h))
        if l == min(c["low"] for c in window):
            lows.append((i, l))

    return highs, lows


def detect_structure(candles):
    """
    Simplified BOS/CHoCH detection:
      - BOS  = price closes beyond the latest swing point in the direction
               of the prevailing trend (trend continuation).
      - CHoCH = price closes beyond a swing point against the prevailing
                trend (potential trend change).
    """
    highs, lows = find_swing_points(candles)

    if len(highs) < 2 or len(lows) < 2:
        return {"bias": "Unknown", "event": None, "last_high": None, "last_low": None}

    last_high, prev_high = highs[-1][1], highs[-2][1]
    last_low, prev_low = lows[-1][1], lows[-2][1]

    if last_high > prev_high and last_low > prev_low:
        trend = "bullish"
    elif last_high < prev_high and last_low < prev_low:
        trend = "bearish"
    else:
        trend = "ranging"

    close = candles[-1]["close"]
    event = None

    if trend == "bullish" and close > last_high:
        event = "BOS_BULLISH"
    elif trend == "bearish" and close < last_low:
        event = "BOS_BEARISH"
    elif trend == "bullish" and close < last_low:
        event = "CHOCH_BEARISH"
    elif trend == "bearish" and close > last_high:
        event = "CHOCH_BULLISH"

    return {"bias": trend, "event": event, "last_high": last_high, "last_low": last_low}


# ---------------------------------------------------------------------------
# Order Blocks
# ---------------------------------------------------------------------------
def find_last_order_block(candles, direction, before_index, search_back=15):
    """direction='bullish' -> last bearish candle before the event (demand OB).
       direction='bearish' -> last bullish candle before the event (supply OB)."""
    for i in range(before_index, max(before_index - search_back, 0), -1):
        c = candles[i]
        if direction == "bullish" and c["close"] < c["open"]:
            return c
        if direction == "bearish" and c["close"] > c["open"]:
            return c
    return None


# ---------------------------------------------------------------------------
# Fair Value Gaps
# ---------------------------------------------------------------------------
def find_recent_fvg(candles, direction, lookback=20):
    """Bullish FVG: candle[i-1].high < candle[i+1].low (gap up).
       Bearish FVG: candle[i-1].low  > candle[i+1].high (gap down)."""
    n = len(candles)
    start = max(1, n - lookback)
    gaps = []

    for i in range(start, n - 1):
        prev_c, next_c = candles[i - 1], candles[i + 1]
        if direction == "bullish" and prev_c["high"] < next_c["low"]:
            gaps.append((prev_c["high"], next_c["low"]))
        if direction == "bearish" and prev_c["low"] > next_c["high"]:
            gaps.append((next_c["high"], prev_c["low"]))

    return gaps[-1] if gaps else None


# ---------------------------------------------------------------------------
# Liquidity sweep
# ---------------------------------------------------------------------------
def detect_liquidity_sweep(candles, highs, lows):
    """Wick beyond a recent swing point followed by a close back inside it."""
    if not highs or not lows:
        return None

    last = candles[-1]
    recent_high, recent_low = highs[-1][1], lows[-1][1]

    if last["high"] > recent_high and last["close"] < recent_high:
        return "SWEEP_HIGH"
    if last["low"] < recent_low and last["close"] > recent_low:
        return "SWEEP_LOW"

    return None


# ---------------------------------------------------------------------------
# Decision engine
# ---------------------------------------------------------------------------
def analyze(candles):
    structure = detect_structure(candles)
    highs, lows = find_swing_points(candles)
    sweep = detect_liquidity_sweep(candles, highs, lows)

    close = candles[-1]["close"]
    event = structure["event"]

    direction = "WAIT"
    confluences = []
    ob = None

    if event in ("BOS_BULLISH", "CHOCH_BULLISH"):
        direction = "BUY"
        confluences.append(event)
        ob = find_last_order_block(candles, "bullish", len(candles) - 1)
        fvg = find_recent_fvg(candles, "bullish")
        if ob:
            confluences.append("ORDER_BLOCK")
        if fvg:
            confluences.append("FVG")
        if sweep == "SWEEP_LOW":
            confluences.append("LIQUIDITY_SWEEP")

    elif event in ("BOS_BEARISH", "CHOCH_BEARISH"):
        direction = "SELL"
        confluences.append(event)
        ob = find_last_order_block(candles, "bearish", len(candles) - 1)
        fvg = find_recent_fvg(candles, "bearish")
        if ob:
            confluences.append("ORDER_BLOCK")
        if fvg:
            confluences.append("FVG")
        if sweep == "SWEEP_HIGH":
            confluences.append("LIQUIDITY_SWEEP")

    if direction in ("BUY", "SELL") and len(confluences) >= 2:
        decision = direction
        confidence = min(95.0, 40.0 + 15.0 * (len(confluences) - 1))
    else:
        decision = "WAIT"
        confidence = 0.0

    entry, stop_loss, take_profit = close, 0.0, 0.0

    if decision == "BUY":
        base = ob["low"] if ob else (structure["last_low"] or close * 0.995)
        risk = max(entry - base, entry * 0.002)
        stop_loss = entry - risk
        take_profit = entry + risk * MIN_RR
    elif decision == "SELL":
        base = ob["high"] if ob else (structure["last_high"] or close * 1.005)
        risk = max(base - entry, entry * 0.002)
        stop_loss = entry + risk
        take_profit = entry - risk * MIN_RR

    return {
        "symbol": BINANCE_SYMBOL.replace("USDT", "USD"),
        "decision": decision,
        "direction": direction if decision != "WAIT" else "WAIT",
        "confidence": round(confidence, 1),
        "market_bias": structure["bias"].capitalize() if structure["bias"] else "Unknown",
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "confluences": confluences,
    }


# ---------------------------------------------------------------------------
# ntfy.sh push (with retries — a transient failure no longer gets silently
# swallowed)
# ---------------------------------------------------------------------------
def _retry_after_seconds(value):
    if not value:
        return None
    try:
        return max(0.0, float(value.strip()))
    except (TypeError, ValueError):
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


def _record_ntfy_result(status, attempts, error=None, http_status=None):
    with State.ntfy_lock:
        data = State.ntfy_delivery
        data["last_status"] = status
        data["last_attempts"] = attempts
        data["last_error"] = str(error) if error else None
        data["last_http_status"] = http_status
        data["last_attempt_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        if status == "delivered":
            data["successes"] += 1
            data["last_success_at"] = data["last_attempt_at"]
        else:
            data["failures"] += 1


def _send_ntfy_serialized(title, message, priority="3", tag="hourglass"):
    if not NTFY_TOPIC:
        error = "NTFY_TOPIC is missing; refusing to send to an unintended default topic."
        print(f"[NTFY CONFIG ERROR] {error}")
        _record_ntfy_result("configuration_error", 0, error=error)
        return False

    with State.ntfy_lock:
        remaining = max(0.0, State.ntfy_blocked_until - time.monotonic())
        if remaining > 0:
            State.ntfy_delivery["deferred"] += 1
            State.ntfy_delivery["cooldown_seconds"] = int(remaining + 0.999)
            State.ntfy_delivery["last_status"] = "rate_limited_cooldown"
            State.ntfy_delivery["last_error"] = f"ntfy cooldown active ({remaining:.0f}s remaining)"
            print(f"[NTFY COOLDOWN] Suppressed; {remaining:.0f}s remaining", flush=True)
            return False
        State.ntfy_delivery["cooldown_seconds"] = 0
    url = f"{NTFY_SERVER}/{NTFY_TOPIC}"
    last_error = None
    last_http_status = None
    attempts_made = 0

    for attempt in range(1, NTFY_MAX_RETRIES + 1):
        attempts_made = attempt
        req = urllib.request.Request(
            url,
            data=message.encode("utf-8"),
            method="POST",
            headers={"Title": title, "Priority": priority, "Tags": tag},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"[NTFY] Accepted by {NTFY_SERVER}/{NTFY_TOPIC} — HTTP {resp.status} (attempt {attempt})")
                with State.ntfy_lock:
                    State.ntfy_consecutive_429 = 0
                    State.ntfy_blocked_until = 0.0
                    State.ntfy_delivery["cooldown_seconds"] = 0
                _record_ntfy_result("delivered", attempt, http_status=resp.status)
                return True
        except urllib.error.HTTPError as exc:
            last_error, last_http_status = exc, exc.code
            if exc.code == 429:
                retry_after = _retry_after_seconds((exc.headers or {}).get("Retry-After"))
                with State.ntfy_lock:
                    State.ntfy_consecutive_429 += 1
                    fallback = min(60 * (2 ** (State.ntfy_consecutive_429 - 1)), 3600)
                    delay = retry_after if retry_after is not None else fallback
                    State.ntfy_blocked_until = max(State.ntfy_blocked_until, time.monotonic() + delay)
                    State.ntfy_delivery["rate_limited"] += 1
                    State.ntfy_delivery["cooldown_seconds"] = int(delay + 0.999)
                last_error = f"HTTP 429; delivery suppressed for {delay:.0f}s"
                print(f"[NTFY 429] No immediate retry; shared cooldown={delay:.0f}s", flush=True)
                break
            elif exc.code in (408, 425, 500, 502, 503, 504):
                delay = min(
                    NTFY_RETRY_DELAY_SECONDS * (2 ** (attempt - 1)),
                    NTFY_MAX_BACKOFF_SECONDS,
                )
                print(f"[NTFY HTTP {exc.code}] Retryable failure; attempt {attempt}/{NTFY_MAX_RETRIES}, wait={delay}s")
                if attempt < NTFY_MAX_RETRIES:
                    time.sleep(delay)
                    continue
            else:
                print(f"[NTFY HTTP {exc.code}] Non-retryable delivery failure: {exc}")
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            delay = min(
                NTFY_RETRY_DELAY_SECONDS * (2 ** (attempt - 1)),
                NTFY_MAX_BACKOFF_SECONDS,
            )
            print(f"[NTFY NETWORK ERROR] Attempt {attempt}/{NTFY_MAX_RETRIES} failed: {exc}")
            if attempt < NTFY_MAX_RETRIES:
                time.sleep(delay)
                continue
        except Exception as exc:
            last_error = exc
            print(f"[NTFY ERROR] Unexpected non-retryable failure: {exc}")
            break

    print(f"[NTFY ERROR] Delivery failed after {attempts_made} attempt(s).")
    _record_ntfy_result("failed", attempts_made, error=last_error, http_status=last_http_status)
    return False


def send_ntfy(title, message, priority="3", tag="hourglass"):
    # One sender at a time: later callers re-check the cooldown only after
    # the preceding HTTP attempt has recorded its result.
    with NTFY_SEND_LOCK:
        return _send_ntfy_serialized(title, message, priority, tag)


def send_entry_notification(signal):
    title = f"{signal['symbol']} {signal['decision']}"
    message = (
        f"Direction: {signal['direction']}\n"
        f"Confidence: {signal['confidence']:.1f}%\n"
        f"Bias: {signal['market_bias']}\n"
        f"Confluences: {', '.join(signal['confluences']) if signal['confluences'] else '-'}\n"
        f"Entry: {signal['entry']:.2f}  SL: {signal['stop_loss']:.2f}  TP: {signal['take_profit']:.2f}"
    )
    tag = "chart_with_upwards_trend" if signal["decision"] == "BUY" else "chart_with_downwards_trend"
    return send_ntfy(title, message, priority="5", tag=tag)


def send_exit_notification(trade, outcome, current_price):
    """outcome: 'TP_HIT' or 'SL_HIT'

    NOTE: ntfy.sh delivers the Title as an HTTP header, and HTTP headers
    must be ASCII/Latin-1 — emoji here would crash the request before it
    ever reaches ntfy.sh. Emoji are safe inside the message body only.
    """
    label = "TAKE PROFIT HIT" if outcome == "TP_HIT" else "STOP LOSS HIT"
    title = f"{trade['symbol']} {label}"
    emoji = "🎯" if outcome == "TP_HIT" else "🛑"
    message = (
        f"{emoji} {label}\n"
        f"Trade: {trade['direction']} opened at {trade['entry']:.2f}\n"
        f"Current price: {current_price:.2f}\n"
        f"SL: {trade['stop_loss']:.2f}  TP: {trade['take_profit']:.2f}"
    )
    tag = "moneybag" if outcome == "TP_HIT" else "warning"
    return send_ntfy(title, message, priority="5", tag=tag)


# ---------------------------------------------------------------------------
# Trade tracking — checks the open trade against the latest price every scan
# ---------------------------------------------------------------------------
def check_active_trade(current_price):
    """Returns True if the trade closed this scan (TP/SL hit)."""
    trade = State.active_trade
    if not trade:
        return False

    outcome = None

    if trade["direction"] == "BUY":
        if current_price <= trade["stop_loss"]:
            outcome = "SL_HIT"
        elif current_price >= trade["take_profit"]:
            outcome = "TP_HIT"
    elif trade["direction"] == "SELL":
        if current_price >= trade["stop_loss"]:
            outcome = "SL_HIT"
        elif current_price <= trade["take_profit"]:
            outcome = "TP_HIT"

    if outcome:
        print(f"[TRADE] {outcome} — {trade['direction']} @ {trade['entry']} (price {current_price})")

        # Any failure in send_exit_notification (network issue, encoding
        # bug, etc.) must NEVER leave active_trade permanently stuck —
        # that would silently block all future signals forever. The
        # trade is always closed and recorded regardless of whether the
        # push notification itself succeeded.
        delivered = False
        try:
            delivered = send_exit_notification(trade, outcome, current_price)
        except Exception as exc:
            print(f"[NTFY ERROR] send_exit_notification crashed: {exc}")

        State.last_closed_trade = {
            **trade,
            "outcome": outcome,
            "exit_price": current_price,
            "notified": delivered,
            "closed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        State.active_trade = None
        return True

    return False


# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Monitoring-only Binance live-price heartbeat
# ---------------------------------------------------------------------------

def fetch_live_price():
    """Fetch Binance ticker price, not an MT5 execution price."""
    url = f"{BINANCE_TICKER_PRICE_URL}?symbol={BINANCE_SYMBOL}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "gti-ai-render-heartbeat/1.0"},
    )
    with _binance_urlopen(req, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    price = float(payload["price"])
    if not (price > 0 and price < float("inf")):
        raise ValueError("Invalid Binance ticker price")
    return price


def send_heartbeat_once():
    """Send monitoring status without reading or changing trade state."""
    price = None
    price_error = None
    try:
        price = fetch_live_price()
    except Exception as exc:
        # A failed price request must not suppress the monitoring heartbeat.
        price_error = str(exc) or exc.__class__.__name__

    now = datetime.now(timezone.utc)

    # Read scanner state, then release its lock before reading delivery metrics.
    with State.lock:
        signal = dict(State.last_signal or {})
        scanner_error = getattr(State, "last_error", None)

    with State.ntfy_lock:
        delivery = dict(State.ntfy_delivery)

    updated = signal.get("updated", "Unknown")
    decision = signal.get("decision", "WAIT")
    bias = signal.get("market_bias", "Unknown")

    try:
        signal_dt = datetime.strptime(
            updated, "%Y-%m-%d %H:%M:%S UTC"
        ).replace(tzinfo=timezone.utc)
        age = max(0, int((now - signal_dt).total_seconds()))
        freshness = (
            "FRESH"
            if age <= max(300, 5 * SCAN_INTERVAL_SECONDS)
            else "STALE"
        )
        age_text = f"{age // 60} minutes"
    except (TypeError, ValueError):
        freshness = "UNKNOWN"
        age_text = "unknown"

    scanner_status = "ERROR" if scanner_error else "ONLINE"
    previous_delivery = delivery.get("last_status", "never")
    if previous_delivery == "delivered":
        delivery_status = "DELIVERED"
    elif previous_delivery == "never":
        delivery_status = "NEVER"
    else:
        delivery_status = "FAILED"

    price_text = f"{price:.2f}" if price is not None else "UNAVAILABLE"
    price_error_text = price_error or "None"

    message = (
        "GTI BTCUSDT LIVE MARKET HEARTBEAT\n"
        "Monitoring only - no broker execution or position verification.\n"
        f"Binance live price: {price_text}\n"
        f"Binance price error: {price_error_text}\n"
        f"Price observation UTC: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Last signal update: {updated}\n"
        f"Signal age: {age_text}\n"
        f"Signal freshness: {freshness}\n"
        f"Last decision: {decision}\n"
        f"Market bias: {bias}\n"
        f"Scanner status: {scanner_status}\n"
        f"Scanner error: {scanner_error or 'None'}\n"
        f"Aggregate ntfy delivery (alerts + heartbeats): {delivery_status}\n"
        f"Aggregate ntfy error: {delivery.get('last_error') or 'None'}\n"
        "Execution mode: MANUAL MT5 ONLY"
    )

    return send_ntfy(
        title="GTI BTCUSDT HEARTBEAT",
        message=message,
        priority="1",
        tag="heartbeat",
    )

def ntfy_heartbeat_loop():
    """Periodic monitoring only; no trade creation or closure."""
    interval = NTFY_HEARTBEAT_INTERVAL_SECONDS

    if interval <= 0:
        print("[HEARTBEAT] disabled", flush=True)
        return

    while True:
        try:
            delivered = send_heartbeat_once()
            print(
                f"[HEARTBEAT] interval={interval}s "
                f"delivery={'OK' if delivered else 'FAILED'}",
                flush=True,
            )
        except Exception as exc:
            print(f"[HEARTBEAT ERROR] {exc}", flush=True)

        time.sleep(interval)


# Scan loop
# ---------------------------------------------------------------------------
def scan_once():
    try:
        candles = fetch_klines()
        result = analyze(candles)
        current_price = candles[-1]["close"]
        now = datetime.now(timezone.utc)
        result["updated"] = now.strftime("%Y-%m-%d %H:%M:%S UTC")

        with State.lock:
            State.last_signal = result
            State.last_error = None

            # 1. Check if the currently tracked trade hit SL/TP — this
            #    always fires immediately, bypassing the notify throttle.
            check_active_trade(current_price)

            # 2. Consider a new entry notification.
            if result["decision"] in ("BUY", "SELL") and State.active_trade is None:
                current_ts = time.time()
                since_success = current_ts - State.last_signal_notify_ts
                since_attempt = current_ts - State.last_signal_attempt_ts

                success_ok = (
                    State.last_signal_notify_ts == 0.0
                    or since_success >= MIN_SIGNAL_NOTIFY_INTERVAL_SECONDS
                )
                retry_ok = (
                    State.last_signal_attempt_ts == 0.0
                    or since_attempt >= SCAN_INTERVAL_SECONDS
                )

                if success_ok and retry_ok:
                    State.last_signal_attempt_ts = current_ts
                    delivered = send_entry_notification(result)

                    State.last_entry_notification = {
                        "direction": result["decision"],
                        "entry": result["entry"],
                        "notified": delivered,
                        "attempted_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    }

                    if delivered:
                        State.last_signal_notify_ts = time.time()
                        State.active_trade = {
                            "symbol": result["symbol"],
                            "direction": result["decision"],
                            "entry": result["entry"],
                            "stop_loss": result["stop_loss"],
                            "take_profit": result["take_profit"],
                            "opened_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "entry_notified": True,
                        }
                    else:
                        print("[TRADE TRACKING] Notification failed; no active trade created.")

                elif not success_ok:
                    print("[THROTTLE] Successful notification cooldown is active.")
                else:
                    print("[RETRY THROTTLE] Waiting for the next scan interval.")

        print("[SCAN]", json.dumps(result, ensure_ascii=False))

    except Exception as exc:
        print(f"[SCAN ERROR] {exc}")
        with State.lock:
            State.last_error = str(exc)


def scan_loop():
    while True:
        scan_once()
        remaining = binance_cooldown_remaining()
        delay = max(SCAN_INTERVAL_SECONDS, remaining)
        if remaining > 0:
            print(f"[SCAN] Binance cooldown; next scan in {delay:.0f}s", flush=True)
        time.sleep(delay)


# ---------------------------------------------------------------------------
# Minimal HTTP server — health check + current signal
# ---------------------------------------------------------------------------
class ServiceHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[HTTP] {self.address_string()} {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            # Snapshot scanner-owned state first, then notification metrics.
            # Lock order is State.lock -> State.ntfy_lock, matching scan_once().
            # Deep copies detach nested mutable values before serialization.
            with State.lock:
                health_data = {
                    "status": "ok" if State.last_error is None else "error",
                    "service": "GTI BTCUSD Binance Signal Service",
                    "last_error": State.last_error,
                    "active_trade": copy.deepcopy(State.active_trade),
                    "last_closed_trade": copy.deepcopy(State.last_closed_trade),
                    "last_entry_notification": copy.deepcopy(State.last_entry_notification),
                    "updated": State.last_signal["updated"],
                }
                with State.ntfy_lock:
                    health_data["ntfy_delivery"] = copy.deepcopy(State.ntfy_delivery)
            with BINANCE_LOCK:
                health_data["binance_data"] = {
                    "last_http_status": BINANCE_LAST_HTTP_STATUS,
                    "last_error": BINANCE_LAST_ERROR,
                    "rate_limit_events": BINANCE_RATE_LIMIT_EVENTS,
                    "cooldown_seconds": int(max(0.0, BINANCE_BLOCKED_UNTIL - time.monotonic()) + 0.999),
                }
            self.send_json(health_data)
            return

        if self.path in ("/", "/api/signal"):
            with State.lock:
                self.send_json(State.last_signal)
            return

        self.send_json({"ok": False, "error": "Not Found"}, 404)


def run_http_server():
    server = ThreadingHTTPServer((HOST, PORT), ServiceHandler)
    print(f"[+] HTTP server listening on port {PORT}")
    server.serve_forever()


def main():
    if not NTFY_TOPIC:
        raise RuntimeError("NTFY_TOPIC environment variable is required; refusing to start with an implicit destination.")
    if not NTFY_SERVER.startswith(("https://", "http://")):
        raise RuntimeError("NTFY_SERVER must be an HTTP(S) URL.")

    print("=" * 60)
    print("GTI BTCUSD BINANCE SIGNAL SERVICE (v3)")
    print("=" * 60)
    print(f"Symbol            : {BINANCE_SYMBOL}")
    print(f"Interval          : {BINANCE_INTERVAL}")
    print(f"Scan every        : {SCAN_INTERVAL_SECONDS}s")
    print(f"Entry notify every: min {MIN_SIGNAL_NOTIFY_INTERVAL_SECONDS}s apart")
    print(f"NTFY topic        : {NTFY_TOPIC}")
    print("=" * 60)

    scanner_thread = threading.Thread(target=scan_loop, daemon=True)
    scanner_thread.start()

    heartbeat_thread = threading.Thread(
        target=ntfy_heartbeat_loop,
        name="ntfy-heartbeat",
        daemon=True,
    )
    heartbeat_thread.start()
    print("[HEARTBEAT] thread started", flush=True)

    run_http_server()


if __name__ == "__main__":
    main()
