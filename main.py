"""
GTI AI
Main Entry Point
Version 1.0
"""

from web.run_dashboard import start_scanner
from web.dashboard_server import run
from threading import Thread


def main() -> None:
    Thread(
        target=start_scanner,
        daemon=True,
    ).start()

    run(
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
