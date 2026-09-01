"""
GTI BTCUSD Binance Signal Service
==================================
Standalone service — fetches BTCUSDT candles directly from the Binance
public data API, runs a lightweight SMC/ICT-style analysis (BOS, CHoCH,
Order Blocks, FVG, liquidity sweeps), and pushes signals straight to ntfy.sh.

Runs entirely on Render. No Termux, no MT5, no external dependency —
pure Python standard library only.

v3: retries failed ntfy.sh deliveries (up to 3 attempts) and always
records the outcome of a closed trade in /health as "last_closed_trade",
so the outcome is visible even if the push notification itself never
reached the phone.
"""

import os
import json
import time
import threading
import urllib.request
import urllib.error
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
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "gti_ai_btcusd_signals")
NTFY_MAX_RETRIES = 3
NTFY_RETRY_DELAY_SECONDS = 5

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

    # Monotonic timestamp (time.time()) of the last new-entry notification.
    last_signal_notify_ts = 0.0


# ---------------------------------------------------------------------------
# Binance market data
# ---------------------------------------------------------------------------
def fetch_klines(symbol=BINANCE_SYMBOL, interval=BINANCE_INTERVAL, limit=CANDLE_LIMIT):
    url = f"{BINANCE_KLINES_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "gti-ai-render/1.0"})

    with urllib.request.urlopen(req, timeout=15) as resp:
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
def send_ntfy(title, message, priority="3", tag="hourglass"):
    url = f"{NTFY_SERVER}/{NTFY_TOPIC}"

    for attempt in range(1, NTFY_MAX_RETRIES + 1):
        req = urllib.request.Request(
            url,
            data=message.encode("utf-8"),
            method="POST",
            headers={"Title": title, "Priority": priority, "Tags": tag},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"[NTFY] Sent to {NTFY_TOPIC} — status {resp.status} (attempt {attempt})")
                return True
        except Exception as exc:
            print(f"[NTFY ERROR] Attempt {attempt}/{NTFY_MAX_RETRIES} failed: {exc}")
            if attempt < NTFY_MAX_RETRIES:
                time.sleep(NTFY_RETRY_DELAY_SECONDS)

    print(f"[NTFY ERROR] Giving up after {NTFY_MAX_RETRIES} attempts.")
    return False


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

            # 2. Consider a new entry notification, but only if:
            #    - the engine found a BUY/SELL
            #    - we're not already tracking an open trade
            #    - at least MIN_SIGNAL_NOTIFY_INTERVAL_SECONDS has passed
            #      since the last entry notification
            if result["decision"] in ("BUY", "SELL") and State.active_trade is None:
                elapsed = time.time() - State.last_signal_notify_ts
                if elapsed >= MIN_SIGNAL_NOTIFY_INTERVAL_SECONDS:
                    delivered = send_entry_notification(result)
                    State.active_trade = {
                        "symbol": result["symbol"],
                        "direction": result["decision"],
                        "entry": result["entry"],
                        "stop_loss": result["stop_loss"],
                        "take_profit": result["take_profit"],
                        "opened_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "entry_notified": delivered,
                    }
                    State.last_signal_notify_ts = time.time()
                else:
                    print(f"[THROTTLE] New {result['decision']} signal suppressed "
                          f"({elapsed:.0f}s since last notify, need {MIN_SIGNAL_NOTIFY_INTERVAL_SECONDS}s)")

        print("[SCAN]", json.dumps(result, ensure_ascii=False))

    except Exception as exc:
        print(f"[SCAN ERROR] {exc}")
        with State.lock:
            State.last_error = str(exc)


def scan_loop():
    while True:
        scan_once()
        time.sleep(SCAN_INTERVAL_SECONDS)


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
            with State.lock:
                self.send_json({
                    "status": "ok" if State.last_error is None else "error",
                    "service": "GTI BTCUSD Binance Signal Service",
                    "last_error": State.last_error,
                    "active_trade": State.active_trade,
                    "last_closed_trade": State.last_closed_trade,
                    "updated": State.last_signal["updated"],
                })
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

    run_http_server()


if __name__ == "__main__":
    main()
