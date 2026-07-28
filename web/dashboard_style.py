"""
GTI AI
Dashboard Style
Version 1.0
"""


class DashboardStyle:
    """
    HTML styling helpers.
    """

    @staticmethod
    def color(decision: str) -> str:
        decision = decision.upper()

        if decision == "BUY":
            return "#00C853"

        if decision == "SELL":
            return "#D50000"

        return "#FFD600"

    @staticmethod
    def html(signal: dict) -> str:
        color = DashboardStyle.color(
            signal.get("decision", "WAIT")
        )

        return f"""
<html>

<head>

<title>GTI AI Dashboard</title>

<meta http-equiv="refresh" content="5">

<style>

body {{
background:#101010;
color:white;
font-family:Arial;
padding:30px;
}}

.card {{
background:#1d1d1d;
padding:20px;
border-radius:15px;
margin-bottom:20px;
}}

.decision {{
font-size:42px;
font-weight:bold;
color:{color};
}}

.value {{
font-size:28px;
}}

</style>

</head>

<body>

<h1>🤖 GTI AI Dashboard</h1>

<div class="card">

<h2>Decision</h2>

<div class="decision">
{signal.get("decision","WAIT")}
</div>

</div>

<div class="card">

<h2>Confidence</h2>

<div class="value">
{signal.get("confidence",0)}%
</div>

</div>

<div class="card">

<h2>Trend</h2>

<div class="value">
{signal.get("trend","Unknown")}
</div>

</div>

<div class="card">

<h2>Updated</h2>

<div class="value">
{signal.get("updated","--")}
</div>

</div>

</body>

</html>
"""
