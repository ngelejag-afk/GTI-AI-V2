"""
GTI AI
Run Dashboard
Version 1.0
"""

from threading import Thread

from scanner.live_market_scanner import LiveMarketScanner
from web.dashboard_server import run


def start_scanner():
    scanner = LiveMarketScanner()
    scanner.run()


if __name__ == "__main__":
    Thread(
        target=start_scanner,
        daemon=True,
    ).start()

    run(host="0.0.0.0", port=8000)
