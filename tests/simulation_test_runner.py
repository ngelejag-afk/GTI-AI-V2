"""
GTI AI
Simulation Test Runner
Version 1.0
"""

from __future__ import annotations

from analysis.performance_monitor import PerformanceMonitor
from execution.simulation_engine import SimulationEngine


def run() -> None:
    """
    Execute a simple simulation test.
    """

    PerformanceMonitor.reset()

    signal = {
        "symbol": "XAUUSD",
        "decision": "BUY",
        "entry": 2350.00,
        "stop_loss": 2345.00,
        "take_profit": 2360.00,
        "confidence": 92,
    }

    print("=" * 50)
    print("GTI AI SIMULATION TEST")
    print("=" * 50)

    SimulationEngine.open_trade(signal)

    prices = [
        2351.00,
        2353.50,
        2356.20,
        2358.90,
        2360.00,
    ]

    for price in prices:
        print(f"Market Price: {price}")
        SimulationEngine.update_price(
            symbol="XAUUSD",
            price=price,
        )

    print("\nOpen Positions")
    print(SimulationEngine.open_positions())

    print("\nPerformance Summary")
    print(PerformanceMonitor.summary())


if __name__ == "__main__":
    run()
