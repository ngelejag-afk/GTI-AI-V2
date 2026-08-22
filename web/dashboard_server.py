import os
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))
SIGNAL_INGEST_TOKEN = os.environ.get("SIGNAL_INGEST_TOKEN", "").strip()


class DashboardState:
    signal = {
        "symbol": "XAUUSD",
        "decision": "WAIT",
        "direction": "WAIT",
        "confidence": 0.0,
        "market_bias": "Unknown",
        "entry": 0.0,
        "stop_loss": 0.0,
        "take_profit": 0.0,
        "timestamp": None,
        "updated": "--:--:-- UTC",
    }


class DashboardServer(BaseHTTPRequestHandler):

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

    def send_html(self, html):
        body = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/health":
            self.send_json({
                "status": "ok",
                "service": "GTI-AI-V2 Dashboard",
                "signal_token": "CONFIGURED" if SIGNAL_INGEST_TOKEN else "NOT_CONFIGURED",
                "updated": DashboardState.signal["updated"]
            })
            return

        if self.path == "/api/signal":
            self.send_json(DashboardState.signal)
            return

        if self.path != "/":
            self.send_json({
                "ok": False,
                "error": "Not Found"
            }, 404)
            return

        s = DashboardState.signal
        decision = s["decision"]

        if decision == "BUY":
            decision_color = "#00E676"
        elif decision == "SELL":
            decision_color = "#FF1744"
        else:
            decision_color = "#FFD600"

        confidence = max(0.0, min(100.0, float(s["confidence"])))

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="5">
<title>GTI-AI-V2 LIVE DASHBOARD</title>

<style>
body {{
    background:#101010;
    color:white;
    font-family:Arial,sans-serif;
    padding:20px;
}}

.card {{
    background:#1d1d1d;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
}}

.decision {{
    font-size:48px;
    font-weight:bold;
    text-align:center;
    color:{decision_color};
}}

.value {{
    font-size:25px;
}}

.signal {{
    font-size:30px;
    font-weight:bold;
}}

table {{
    width:100%;
}}

td {{
    padding:8px;
}}
</style>
</head>

<body>

<h1>🤖 GTI-AI-V2 LIVE DASHBOARD</h1>

<div class="card">
<h2>Decision</h2>
<div class="decision">{decision}</div>
</div>

<div class="card">
<h2>Symbol</h2>
<div class="signal">{s["symbol"]}</div>
</div>

<div class="card">
<h2>Confidence</h2>

<div style="
width:100%;
background:#333;
border-radius:10px;
overflow:hidden;
height:25px;
">

<div style="
width:{confidence}%;
background:{decision_color};
height:25px;
text-align:center;
font-weight:bold;
">

{confidence:.1f}%

</div>
</div>
</div>

<div class="card">
<h2>Market Bias</h2>
<div class="value">{s["market_bias"]}</div>
</div>

<div class="card">
<h2>Trade Levels</h2>

<table>
<tr>
<td><b>Entry</b></td>
<td>{s["entry"]:.2f}</td>
</tr>

<tr>
<td><b>Stop Loss</b></td>
<td>{s["stop_loss"]:.2f}</td>
</tr>

<tr>
<td><b>Take Profit</b></td>
<td>{s["take_profit"]:.2f}</td>
</tr>
</table>
</div>

<div class="card">
<h2>Direction</h2>
<div class="value">{s["direction"]}</div>
</div>

<div class="card">
<h2>Last Updated</h2>
<div class="value">{s["updated"]}</div>
</div>

<div class="card">
<h2>System</h2>

<p><b>Signal Engine:</b> TERMUX</p>
<p><b>MT5 Execution:</b> DISABLED</p>
<p><b>Dashboard:</b> RENDER</p>
<p><b>Auto Refresh:</b> 5 seconds</p>
<p><b>Signal API:</b> ONLINE</p>

</div>

</body>
</html>
"""

        self.send_html(html)

    def do_POST(self):

        if self.path != "/api/signal":
            self.send_json({
                "ok": False,
                "error": "Not Found"
            }, 404)
            return

        if not SIGNAL_INGEST_TOKEN:
            self.send_json({
                "ok": False,
                "error": "SIGNAL_INGEST_TOKEN is not configured on Render"
            }, 503)
            return

        received_token = self.headers.get("X-Signal-Token", "")

        if received_token != SIGNAL_INGEST_TOKEN:
            self.send_json({
                "ok": False,
                "error": "Unauthorized"
            }, 401)
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )

            if content_length <= 0:
                raise ValueError("Empty request body")

            raw_body = self.rfile.read(content_length)
            data = json.loads(raw_body.decode("utf-8"))

            now = datetime.now(timezone.utc)

            decision = str(
                data.get("decision", "WAIT")
            ).upper()

            direction = str(
                data.get(
                    "direction",
                    decision
                )
            ).upper()

            DashboardState.signal = {
                "symbol": data.get(
                    "symbol",
                    "XAUUSD"
                ),

                "decision": decision,

                "direction": direction,

                "confidence": float(
                    data.get(
                        "confidence",
                        0
                    )
                ),

                "market_bias": data.get(
                    "market_bias",
                    data.get(
                        "trend",
                        "Unknown"
                    )
                ),

                "entry": float(
                    data.get(
                        "entry",
                        0
                    )
                ),

                "stop_loss": float(
                    data.get(
                        "stop_loss",
                        0
                    )
                ),

                "take_profit": float(
                    data.get(
                        "take_profit",
                        0
                    )
                ),

                "timestamp": int(
                    now.timestamp()
                ),

                "updated": now.strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
            }

            print(
                "[SIGNAL UPDATE]",
                json.dumps(
                    DashboardState.signal,
                    ensure_ascii=False
                )
            )

            self.send_json({
                "ok": True,
                "message": "Signal updated",
                "signal": DashboardState.signal
            })

        except Exception as exc:

            print(f"[POST ERROR] {exc}")

            self.send_json({
                "ok": False,
                "error": str(exc)
            }, 400)


def run():

    print("=" * 60)
    print("GTI-AI-V2 DASHBOARD SERVER")
    print("=" * 60)
    print(f"HOST : {HOST}")
    print(f"PORT : {PORT}")
    print(
        "SIGNAL TOKEN : "
        + (
            "CONFIGURED"
            if SIGNAL_INGEST_TOKEN
            else "NOT CONFIGURED"
        )
    )
    print("=" * 60)

    server = ThreadingHTTPServer(
        (HOST, PORT),
        DashboardServer
    )

    print(
        f"[+] Dashboard listening on port {PORT}"
    )

    server.serve_forever()


if __name__ == "__main__":
    run()
