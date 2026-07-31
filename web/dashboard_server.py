"""
GTI AI
Dashboard Server
Version 2.1
"""

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from execution.statistics_engine import StatisticsEngine
from web.dashboard_data import DashboardData
from web.dashboard_history import DashboardHistory
from web.dashboard_style import DashboardStyle


class DashboardServer(BaseHTTPRequestHandler):
    """
    GTI AI Dashboard Server.
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
        data = DashboardData.build(self.signal)

        stats = data["statistics"]
        account = data["account"]
        positions = data["positions"]
        performance = data["performance"]

        trading_stats = StatisticsEngine.summary()

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

            <div class="card">
                <h2>Trading Statistics</h2>
                <p><b>Total Trades:</b> {trading_stats['total_trades']}</p>
                <p><b>Wins:</b> {trading_stats['wins']}</p>
                <p><b>Losses:</b> {trading_stats['losses']}</p>
                <p><b>Breakeven:</b> {trading_stats['breakeven']}</p>
                <p><b>Win Rate:</b> {trading_stats['win_rate']}%</p>
                <p><b>Profit Factor:</b> {trading_stats['profit_factor']}</p>
                <p><b>Consecutive Wins:</b> {trading_stats['consecutive_wins']}</p>
                <p><b>Consecutive Losses:</b> {trading_stats['consecutive_losses']}</p>
                <p><b>Gross Profit:</b> {trading_stats['gross_profit']}</p>
                <p><b>Gross Loss:</b> {trading_stats['gross_loss']}</p>
            </div>

            <div class="card">
                <h2>AI Performance</h2>
                <p><b>Total Trades:</b> {performance['total_trades']}</p>
                <p><b>Wins:</b> {performance['wins']}</p>
                <p><b>Losses:</b> {performance['losses']}</p>
                <p><b>Breakeven:</b> {performance['breakeven']}</p>
                <p><b>Win Rate:</b> {performance['win_rate']}%</p>
                <p><b>Average Confidence:</b> {performance['average_confidence']}%</p>
            </div>

            <div class="card">
                <h2>Account</h2>
                <p><b>Connected:</b> {account['connected']}</p>
                <p><b>Balance:</b> {account['balance']}</p>
                <p><b>Equity:</b> {account['equity']}</p>
                <p><b>Free Margin:</b> {account['free_margin']}</p>
                <p><b>Leverage:</b> {account['leverage']}</p>
            </div>

            <div class="card">
                <h2>Open Positions</h2>
                <p><b>Total:</b> {positions['total_positions']}</p>
                <p><b>BUY:</b> {positions['buy_positions']}</p>
                <p><b>SELL:</b> {positions['sell_positions']}</p>
                <p><b>Floating P/L:</b> {positions['floating_profit']}</p>
            </div>

            <div class="card">
                <h2>Signal Statistics</h2>
                <p><b>Total:</b> {stats['TOTAL']}</p>
                <p><b>BUY:</b> {stats['BUY']}</p>
                <p><b>SELL:</b> {stats['SELL']}</p>
                <p><b>WAIT:</b> {stats['WAIT']}</p>
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
    """
    Start the dashboard server.
    """

    server = HTTPServer((host, port), DashboardServer)

    print("=" * 50)
    print(" GTI AI DASHBOARD")
    print("=" * 50)
    print(f"Running on http://{host}:{port}")
    print("=" * 50)

    server.serve_forever()
