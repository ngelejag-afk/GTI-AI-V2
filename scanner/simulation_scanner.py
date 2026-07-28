"""
GTI AI
Simulation Scanner
Version 1.0
"""

from __future__ import annotations

import time

from risk.stop_loss_engine import StopLossEngine
from risk.take_profit_engine import TakeProfitEngine
from scanner.simulation_engine import SimulationEngine
from web.dashboard_server import DashboardServer


class SimulationScanner:
    """
    Runs the dashboard using simulated market signals.
    """

    def __init__(self, interval: int = 5) -> None:
        self.interval = interval

    def run(self) -> None:
        print("=" * 45)
        print(" GTI AI SIMULATION MODE")
        print("=" * 45)
        print(f"Refresh : {self.interval} seconds")
        print("=" * 45)

        while True:
            signal = SimulationEngine.next_signal()

            entry = signal["entry"]

            stop_loss = StopLossEngine.calculate(
                entry=entry,
                decision=signal["decision"],
            )

            take_profit = TakeProfitEngine.calculate(
                entry=entry,
                stop_loss=stop_loss,
                decision=signal["decision"],
            )

            signal["stop_loss"] = stop_loss
            signal["take_profit"] = take_profit

            DashboardServer.update(signal)

            print()
            print("=" * 45)
            print(" SIMULATION SIGNAL")
            print("=" * 45)
            print(f"Decision     : {signal['decision']}")
            print(f"Confidence   : {signal['confidence']}%")
            print(f"Trend        : {signal['market_bias']}")
            print(f"Entry        : {signal['entry']}")
            print(f"Stop Loss    : {signal['stop_loss']}")
            print(f"Take Profit  : {signal['take_profit']}")
            print("=" * 45)

            time.sleep(self.interval)
