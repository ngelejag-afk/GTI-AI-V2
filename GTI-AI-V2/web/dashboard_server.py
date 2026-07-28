"""
GTI AI
Dashboard Server
Version 1.0
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime


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
        html = f"""
        <html>
        <head>
            <title>GTI AI Dashboard</title>
            <meta http-equiv="refresh" content="5">
        </head>
        <body style="font-family:Arial;padding:40px;background:#111;color:white;">
            <h1>GTI AI Dashboard</h1>

            <h2>Decision</h2>
            <h1>{self.signal['decision']}</h1>

            <h2>Confidence</h2>
            <h1>{self.signal['confidence']}%</h1>

            <h2>Trend</h2>
            <h2>{self.signal['trend']}</h2>

            <h3>Updated</h3>
            <p>{self.signal['updated']}</p>

        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


def run(host: str = "0.0.0.0", port: int = 8000):
    server = HTTPServer((host, port), DashboardServer)

    print("=" * 40)
    print("GTI AI Dashboard")
    print(f"http://{host}:{port}")
    print("=" * 40)

    server.serve_forever()
