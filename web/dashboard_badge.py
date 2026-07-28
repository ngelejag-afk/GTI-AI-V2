"""
GTI AI
Dashboard Badge
Version 1.0
"""


class DashboardBadge:
    """
    Creates a colored BUY / SELL / WAIT badge.
    """

    @staticmethod
    def html(decision: str) -> str:
        decision = decision.upper()

        if decision == "BUY":
            color = "#00C853"

        elif decision == "SELL":
            color = "#D50000"

        else:
            color = "#FFD600"

        return f"""
        <div style="
            background:{color};
            color:white;
            padding:18px;
            border-radius:14px;
            text-align:center;
            font-size:34px;
            font-weight:bold;
            margin-bottom:20px;
        ">
            {decision}
        </div>
        """
