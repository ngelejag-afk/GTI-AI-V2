from __future__ import annotations

"""
GTI AI
Main Controller
Version 1.0
"""


import threading

from controller.system_status import SystemStatus
from scanner.live_market_scanner import LiveMarketScanner
from scanner.simulation_scanner import SimulationScanner
from web.dashboard_server import run as run_dashboard


class GTIController:
    """
    Main controller for GTI AI V2.
    Responsible for starting and managing system services.
    """

    def __init__(
        self,
        simulation_mode: bool = True,
        dashboard_host: str = "0.0.0.0",
        dashboard_port: int = 8000,
    ) -> None:
        self.simulation_mode = simulation_mode
        self.dashboard_host = dashboard_host
        self.dashboard_port = dashboard_port

    def _start_dashboard(self) -> None:
        run_dashboard(
            host=self.dashboard_host,
            port=self.dashboard_port,
        )

    def _start_scanner(self) -> None:
        if self.simulation_mode:
            SimulationScanner().run()
        else:
            LiveMarketScanner().run()

    def start(self) -> None:
        """
        Start GTI AI services.
        """

        print("=" * 50)
        print(" GTI AI V2")
        print("=" * 50)

        status = SystemStatus.get_status()

        print(f"System : {status['system']}")
        print(f"Status : {status['status']}")
        print("=" * 50)

        scanner_thread = threading.Thread(
            target=self._start_scanner,
            daemon=True,
        )

        scanner_thread.start()

        self._start_dashboard()
