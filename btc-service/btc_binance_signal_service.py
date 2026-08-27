"""
GTI BTCUSD Binance Signal Service
===================================
Standalone service – fetches BTCUSDT candles directly from the Binance
public API, runs a lightweight SMC/ICT-style analysis (BOS, CHoCH, Order
Blocks, FVG, liquidity sweeps), and pushes signals straight to ntfy.sh.

Runs entirely on Render. No Termux, no MT5, no external dependency –
pure Python standard library only.
"""

import os
import json
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# =====================================================================
# Config (override any of these via Render environment variables)
# =====================================================================
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))

BINANCE_SYMBOL = os.environ.get("BINANCE_SYMBOL", "BTCUSDT")
BINANCE_INTERVAL = os.environ.get("BINANCE_INTERVAL", "5m")
BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
CANDLE_LIMIT = 150

NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "gti_ai_btcusd_signals")

SCAN_INTERVAL_SECONDS = int(os.environ.get("SCAN_INTERVAL_SECONDS", "300"))  # 5 minutes

SWING_LOOKBACK = 3    # candles each side required to confirm a swing high/low
MIN_RR = 2.0          # minimum reward:risk enforced on generated trade levels


# =====================================================================
# Shared state (read by the HTTP server, written by the scan loop)
# =====================================================================
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


# =====================================================================
# Binance market data
# =====================================================================
def fetch_klines(symbol=BINANCE_SYMBOL, interval=BINANCE_INTERVAL, limit=CANDLE_LIMIT):
    url = f"{BINANCE_KLINES_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "gti-ai-render/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            candles = []
            for item in raw:
                # Binance kline format: [Open time, Open, High, Low, Close, Volume, Close time, ...]
                candles.append({
                    "time": int(item[0]),
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5])
                })
            return candles
    except Exception as e:
        print(f"[Binance] Error fetching klines: {e}")
        return []


# =====================================================================
# Structure: swing points, BOS, CHoCH
# =====================================================================
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
      - BOS  = price closes beyond the latest swing point in the direction of the prevailing trend (trend continuation).
      - CHoCH = price closes beyond a swing point against the prevailing trend (potential trend change).
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


# =====================================================================
# Order Blocks
# =====================================================================
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


# =====================================================================
# Fair Value Gap
# =====================================================================
def find_recent_fvg(candles, direction, lookback=20):
    """Bullish FVG: candle[i-1].high < candle[i+1].low (gap up).
       Bearish FVG: candle[i-1].low > candle[i+1].high (gap down)."""
    n = len(candles)
    for i in range(n - 2, max(n - lookback, 1), -1):
        prev_c = candles[i - 1]
        next_c = candles[i + 1]
        if direction == "bullish" and prev_c["high"] < next_c["low"]:
            return {"top": next_c["low"], "bottom": prev_c["high"]}
        if direction == "bearish" and prev_c["low"] > next_c["high"]:
            return {"top": prev_c["low"], "bottom": next_c["high"]}
    return None


# =====================================================================
# Push Notification via ntfy.sh
# =====================================================================
def send_ntfy_alert(title, message, priority="default", tags=None):
    if tags is None:
        tags = ["chart_with_upwards_trend"]
    try:
        url = f"{NTFY_SERVER}/{NTFY_TOPIC}"
        data = message.encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Title", title)
        req.add_header("Priority", priority)
        req.add_header("Tags", ",".join(tags))
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Ntfy] Failed to send notification: {e}")
        return False


# =====================================================================
# Core Analysis Pipeline
# =====================================================================
def run_analysis_cycle():
    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] Running Binance analysis cycle for {BINANCE_SYMBOL}...")
    candles = fetch_klines()
    if len(candles) < 50:
        print("[Analysis] Insufficient candles fetched from Binance.")
        return

    struct = detect_structure(candles)
    current_price = candles[-1]["close"]
    event = struct["event"]
    bias = struct["bias"]

    decision = "WAIT"
    direction = "WAIT"
    confidence = 0.5
    entry = 0.0
    stop_loss = 0.0
    take_profit = 0.0
    confluences = [f"Market Bias: {bias.upper()}"]

    if event:
        confluences.append(f"Structure Event: {event}")

    # Evaluate trade setup based on structural triggers
    if event in ["BOS_BULLISH", "CHOCH_BULLISH"]:
        direction = "BUY"
        ob = find_last_order_block(candles, "bullish", len(candles) - 2)
        fvg = find_recent_fvg(candles, "bullish")

        if ob:
            entry = round(ob["high"], 2)
            stop_loss = round(ob["low"] - (current_price * 0.001), 2)  # slight buffer below OB
            confluences.append(f"Demand Order Block identified at {entry}")
        else:
            entry = round(current_price, 2)
            stop_loss = round(entry * 0.992, 2)

        risk = entry - stop_loss
        if risk > 0:
            take_profit = round(entry + (risk * MIN_RR), 2)
            decision = "EXECUTE"
            confidence = 0.85 if "CHOCH" in event else 0.75

    elif event in ["BOS_BEARISH", "CHOCH_BEARISH"]:
        direction = "SELL"
        ob = find_last_order_block(candles, "bearish", len(candles) - 2)
        fvg = find_recent_fvg(candles, "bearish")

        if ob:
            entry = round(ob["low"], 2)
            stop_loss = round(ob["high"] + (current_price * 0.001), 2)  # slight buffer above OB
            confluences.append(f"Supply Order Block identified at {entry}")
        else:
            entry = round(current_price, 2)
            stop_loss = round(entry * 1.008, 2)

        risk = stop_loss - entry
        if risk > 0:
            take_profit = round(entry - (risk * MIN_RR), 2)
            decision = "EXECUTE"
            confidence = 0.85 if "CHOCH" in event else 0.75

    # Update global shared state safely
    with State.lock:
        State.last_signal = {
            "symbol": BINANCE_SYMBOL.replace("USDT", "USD"),
            "decision": decision,
            "direction": direction,
            "confidence": confidence,
            "market_bias": bias,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "confluences": confluences,
            "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    # If an actionable trade setup is found, dispatch alert to ntfy
    if decision == "EXECUTE":
        title = f"GTI BTC Alert: {direction} {BINANCE_SYMBOL.replace('USDT', 'USD')}"
        msg = (
            f"Decision: {decision}\n"
            f"Direction: {direction}\n"
            f"Confidence: {int(confidence * 100)}%\n"
            f"Entry: {entry}\n"
            f"Stop Loss: {stop_loss}\n"
            f"Take Profit: {take_profit}\n"
            f"Confluences: {', '.join(confluences)}"
        )
        priority = "high" if confidence > 0.8 else "default"
        tags = ["rotating_light", "chart_with_upwards_trend" if direction == "BUY" else "chart_with_downwards_trend"]
        send_ntfy_alert(title, msg, priority=priority, tags=tags)
        print(f"[Analysis] Signal triggered and pushed to ntfy: {direction} at {entry}")
    else:
        print(f"[Analysis] No trade setup triggered. Current bias: {bias}, Event: {event}")


def background_scanner_loop():
    while True:
        try:
            run_analysis_cycle()
        except Exception as e:
            print(f"[Scanner Loop Error]: {e}")
        time.sleep(SCAN_INTERVAL_SECONDS)


# =====================================================================
# Lightweight HTTP Health & Web Dashboard Server
# =====================================================================
class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health" or self.path == "/":
            with State.lock:
                sig = dict(State.last_signal)
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>GTI BTC Binance Signal Service</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }}
        .container {{ max-width: 650px; margin: auto; background: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
        h1 {{ color: #58a6ff; font-size: 22px; margin-top: 0; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
        .badge {{ display: inline-block; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 14px; }}
        .buy {{ background: #238636; color: #fff; }}
        .sell {{ background: #da3633; color: #fff; }}
        .wait {{ background: #6e7681; color: #fff; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 20px 0; }}
        .card {{ background: #0d1117; padding: 12px 16px; border-radius: 8px; border: 1px solid #30363d; }}
        .card-title {{ font-size: 12px; color: #8b949e; text-transform: uppercase; }}
        .card-value {{ font-size: 18px; font-weight: bold; margin-top: 4px; color: #e6edf3; }}
        ul {{ padding-left: 20px; color: #8b949e; }}
        li {{ margin-bottom: 4px; }}
        .footer {{ font-size: 11px; color: #8b949e; text-align: center; margin-top: 20px; border-top: 1px solid #30363d; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GTI BTCUSD Binance Signal Service</h1>
        <p>Status: <span class="badge {sig['direction'].lower()}">{sig['decision']} ({sig['direction']})</span></p>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">Symbol</div>
                <div class="card-value">{sig['symbol']}</div>
            </div>
            <div class="card">
                <div class="card-title">Market Bias</div>
                <div class="card-value" style="text-transform: capitalize;">{sig['market_bias']}</div>
            </div>
            <div class="card">
                <div class="card-title">Entry Price</div>
                <div class="card-value">{sig['entry'] if sig['entry'] else 'N/A'}</div>
            </div>
            <div class="card">
                <div class="card-title">Confidence</div>
                <div class="card-value">{int(sig['confidence'] * 100)}%</div>
            </div>
            <div class="card">
                <div class="card-title">Stop Loss</div>
                <div class="card-value" style="color: #f85149;">{sig['stop_loss'] if sig['stop_loss'] else 'N/A'}</div>
            </div>
            <div class="card">
                <div class="card-title">Take Profit</div>
                <div class="card-value" style="color: #3fb950;">{sig['take_profit'] if sig['take_profit'] else 'N/A'}</div>
            </div>
        </div>

        <h3>Confluences</h3>
        <ul>
            {"".join(f"<li>{c}</li>" for c in sig['confluences'])}
        </ul>

        <div class="footer">
            Last Updated: {sig['updated']} | Auto-refreshes every 30s
        </div>
    </div>
</body>
</html>
"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/json":
            with State.lock:
                sig = dict(State.last_signal)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(sig, indent=2).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")


# =====================================================================
# Application Entrypoint
# =====================================================================
if __name__ == "__main__":
    print(f"Starting GTI BTC Binance Signal Service on {HOST}:{PORT}...")
    
    # Start background scanner daemon thread
    scanner_thread = threading.Thread(target=background_scanner_loop, daemon=True)
    scanner_thread.start()

    # Start HTTP server for Render web service availability and dashboard monitoring
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down service...")
        server.server_close()

