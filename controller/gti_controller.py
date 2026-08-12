from __future__ import annotations

"""
GTI AI Main Controller
Version 1.0
"""

import threading
from controller.system_status import SystemStatus
from utils.notifier import send_ntfy_signal

class GTIController:
    def __init__(self, simulation_mode: bool = True, dashboard_host: str = "0.0.0.0", dashboard_port: int = 8000):
        self.simulation_mode = simulation_mode
        self.dashboard_host = dashboard_host
        self.dashboard_port = dashboard_port

    def _start_scanner(self):
        # Scanner background logic
        pass

    def _start_dashboard(self):
        print(f"Dashboard started on {self.dashboard_host}:{self.dashboard_port}...")

    def start(self):
        print("=" * 50)
        print(" GTI AI V2")
        print("=" * 50)

        try:
            status = SystemStatus.get_status()
            print(f"System : {status.get('system', 'OK')}")
            print(f"Status : {status.get('status', 'Running')}")
        except Exception:
            pass
        print("=" * 50)

        scanner_thread = threading.Thread(
            target=self._start_scanner,
            daemon=True,
        )
        scanner_thread.start()

        self._start_dashboard()

        # Tuma taarifa kupitia ntfy mfumo unapoanza
        try:
            send_ntfy_signal("GTI-AI-V2", "START", "System Started Successfully", "", "", "INFO")
            print("Ntfy startup notification sent!")
        except Exception as e:
            print(f"Ntfy error: {e}")

if __name__ == "__main__":
    controller = GTIController()
    controller.start()
