"""
GTI AI
Dashboard Server
Version 1.2
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
        "updated": "--:--:--",
    }

    @classmethod
    def update(cls, signal: dict) -> None:
        cls.signal = {
            "decision": signal.get("decision", "WAIT"),
            "confidence": signal.get("confidence", 0),
            "trend": signal.get("market_bias", "Unknown"),
            "updated": datetime.now().strftime("%H:%M:%S"),
        }

        DashboardHistory.add(cls.signal)

    def do_GET(self):
        page = DashboardStyle.html(self.signal)

        page = page.replace(
            "</body>",
            f"""
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
