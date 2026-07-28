"""
GTI AI
Terminal Dashboard
Version 1.0
"""

from __future__ import annotations

from datetime import datetime


class TerminalDashboard:
    """
    Displays the latest GTI AI analysis in the terminal.
    """

    @staticmethod
    def show(
        symbol: str,
        result: dict,
        session: str = "UNKNOWN",
        history_count: int = 0,
    ) -> None:
        """
        Display a formatted dashboard.
        """

        reasons = result.get("reasons", [])

        print()
        print("=" * 45)
        print("          GTI AI LIVE DASHBOARD")
        print("=" * 45)
        print("Status      : 🟢 RUNNING")
        print(f"Symbol      : {symbol}")
        print(f"Session     : {session}")
        print()
        print(f"Decision    : {result.get('decision', 'WAIT')}")
        print(f"Confidence  : {result.get('confidence', 0)}%")
        print(f"Bullish     : {result.get('bullish_votes', 0)}")
        print(f"Bearish     : {result.get('bearish_votes', 0)}")
        print()

        if reasons:
            print("Reasons")
            print("-" * 45)

            for reason in reasons:
                print(f"✔ {reason}")

            print()

        print(f"Signals Saved : {history_count}")
        print(
            f"Updated       : "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("=" * 45)
        print()
