"""
GTI AI
Live Scanner Entry Point
Version 1.0
"""

from scanner.live_market_scanner import LiveMarketScanner


def main() -> None:
    """
    Start the GTI AI live market scanner.
    """

    scanner = LiveMarketScanner(
        symbol="XAUUSD",
        bars=500,
        interval=5,
    )

    scanner.run()


if __name__ == "__main__":
    main()
