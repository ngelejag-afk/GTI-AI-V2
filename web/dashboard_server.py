
"""
GTI AI
Dashboard Server
Version 1.3
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

from web.dashboard_style import DashboardStyle
from web.dashboard_history import DashboardHistory


class DashboardServer(BaseHTTPRequestHandler):
    """
    Simple browser dashboard.
    """

    signal = {
        "decision": "WAIT",
        "confidence": 0,
        "trend": "Unknown",
        "entry": 0.0,
        "stop_loss": 0.0,
        "take_profit": 0.0,
        "updated": "--:--:--",
    }

    @classmethod
    def update(cls, signal: dict) -> None:
        cls.signal = {
            "decision": signal.get("decision", "WAIT"),
            "confidence": signal.get("confidence", 0),
            "trend": signal.get("market_bias", "Unknown"),
            "entry": signal.get("entry", 0.0),
            "stop_loss": signal.get("stop_loss", 0.0),
            "take_profit": signal.get("take_profit", 0.0),
            "updated": datetime.now().strftime("%H:%M:%S"),
        }

        DashboardHistory.add(cls.signal)

    def do_GET(self):
        page = DashboardStyle.html(self.signal)

        page = page.replace(
            "</body>",
            f"""
            <div class="card">
                <h2>Trade Levels</h2>
                <p><b>Entry:</b> {self.signal['entry']}</p>
                <p><b>Stop Loss:</b> {self.signal['stop_loss']}</p>
                <p><b>Take Profit:</b> {self.signal['take_profit']}</p>
            </div>

            <div style="margin-top:30px;">
                <h2>Recent Signals</h2>
                {DashboardHistory.html()}
            </div>

            </body>
            """,
        )

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(page.encode())


def run(host: str = "0.0.0.0", port: int = 8000):
    server = HTTPServer((host, port), DashboardServer)

    print("=" * 40)
    print(" GTI AI DASHBOARD")
    print("=" * 40)
    print(f"Running on http://{host}:{port}")
    print("=" * 40)

    server.serve_forever()
