"""
GTI AI
Dashboard Server
Version 1.1
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

from web.dashboard_style import DashboardStyle


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

    def do_GET(self):
        html = DashboardStyle.html(self.signal)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


def run(host: str = "0.0.0.0", port: int = 8000):
    server = HTTPServer((host, port), DashboardServer)

    print("=" * 40)
    print(" GTI AI DASHBOARD")
    print("=" * 40)
    print(f"Running on http://{host}:{port}")
    print("=" * 40)

    server.serve_forever()
