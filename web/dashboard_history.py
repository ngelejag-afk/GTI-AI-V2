"""
GTI AI
Dashboard History
Version 1.0
"""


class DashboardHistory:
    """
    Stores the latest dashboard signals.
    """

    _signals = []

    @classmethod
    def add(cls, signal: dict) -> None:
        cls._signals.insert(0, signal.copy())
        cls._signals = cls._signals[:10]

    @classmethod
    def html(cls) -> str:
        if not cls._signals:
            return "<p>No signals yet.</p>"

        rows = []

        for signal in cls._signals:
            rows.append(
                f"""
                <tr>
                    <td>{signal.get('updated', '--')}</td>
                    <td>{signal.get('decision', 'WAIT')}</td>
                    <td>{signal.get('confidence', 0)}%</td>
                    <td>{signal.get('trend', 'Unknown')}</td>
                </tr>
                """
            )

        return f"""
        <table style="width:100%;border-collapse:collapse;">
            <tr>
                <th>Time</th>
                <th>Decision</th>
                <th>Confidence</th>
                <th>Trend</th>
            </tr>

            {''.join(rows)}

        </table>
        """
