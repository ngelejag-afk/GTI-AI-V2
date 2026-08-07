from __future__ import annotations
"""
GTI AI
Analytics Engine
Version 1.0
"""


import csv
from pathlib import Path


class AnalyticsEngine:
    """
    Reads the trade journal and produces analytics.
    """

    FILE = Path("trade_journal.csv")

    @classmethod
    def summary(cls) -> dict:
        if not cls.FILE.exists():
            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "breakeven": 0,
                "net_profit": 0.0,
                "average_profit": 0.0,
            }

        wins = 0
        losses = 0
        breakeven = 0
        total = 0
        net_profit = 0.0

        with cls.FILE.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                total += 1

                result = row["result"].upper()
                profit = float(row["profit"])

                net_profit += profit

                if result == "WIN":
                    wins += 1
                elif result == "LOSS":
                    losses += 1
                else:
                    breakeven += 1

        average_profit = (
            net_profit / total
            if total
            else 0.0
        )

        return {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "breakeven": breakeven,
            "net_profit": round(net_profit, 2),
            "average_profit": round(
                average_profit,
                2,
            ),
        }
