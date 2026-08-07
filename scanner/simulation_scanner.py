from __future__ import annotations
"""
GTI AI
Simulation Scanner
Version 2.0
"""

import time
from config.settings import Settings
from execution.session_filter import SessionFilter
from execution.spread_filter import SpreadFilter
from execution.risk_manager import RiskManager


class SimulationScanner:
    """
    Simulates live scanning cycles for strategy analysis and UI telemetry.
    """

    def __init__(self, interval: int = 5) -> None:
        self.interval = interval

    def run(self) -> None:
        print("========================================")
        print(" GTI AI SIMULATION SCANNER")
        print("========================================")

        while True:
            # Dynamic Filter Validation
            spread_res = SpreadFilter.validate(0)
            session_res = SessionFilter.validate()
            risk_res = RiskManager.validate(open_trades=0)

            spread_status = "PASSED" if spread_res["valid"] else "BLOCKED"
            session_status = "PASSED" if session_res["valid"] else "BLOCKED"
            risk_status = "PASSED" if risk_res["valid"] else "BLOCKED"

            trade_allowed = "YES" if (spread_res["valid"] and session_res["valid"] and risk_res["valid"]) else "NO"

            print("\n========================================")
            print(" GTI AI SIGNAL")
            print("========================================")
            print(f"Decision       : WAIT")
            print(f"Confidence     : 0%")
            print(f"Trend          : UNKNOWN")
            print(f"Entry          : 0.0")
            print(f"Stop Loss      : 0.0")
            print(f"Take Profit    : 0.0")
            print(f"Lot Size       : 0.0")
            print(f"Risk Amount    : 0.0")
            print(f"Risk Reward    : 1:0")
            print(f"ATR            : 0.0")
            print(f"Spread         : 0")
            print(f"Spread Status  : {spread_status}")
            print(f"Session        : {session_res.get('session', 'UNKNOWN')}")
            print(f"Session Status : {session_status}")
            print(f"Risk Status    : {risk_status}")
            print(f"Trade Allowed  : {trade_allowed}")
            print(f"Open Positions : 0")
            print(f"Trade History  : 0")
            print("========================================")

            time.sleep(self.interval)
