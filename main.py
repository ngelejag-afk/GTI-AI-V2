"""
GTI AI
Main Entry Point
Version 2.0
"""

from threading import Thread

from scanner.simulation_scanner import SimulationScanner
from web.dashboard_server import run


def start_simulation() -> None:
    """
    Starts the simulation scanner.
    """
    scanner = SimulationScanner(interval=5)
    scanner.run()


def main() -> None:
    Thread(
        target=start_simulation,
        daemon=True,
    ).start()

    run(
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
