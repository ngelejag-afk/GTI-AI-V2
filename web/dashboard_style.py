"""
GTI AI
Dashboard Style
Version 1.1
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
    def progress(confidence: int) -> str:
        color = "#00C853"

        if confidence < 70:
            color = "#FFD600"

        if confidence < 40:
            color = "#D50000"

        return f"""
        <div style="
            width:100%;
            background:#333;
            border-radius:10px;
            overflow:hidden;
            height:22px;
        ">
            <div style="
                width:{confidence}%;
                background:{color};
                height:22px;
                text-align:center;
                color:white;
                font-weight:bold;
            ">
                {confidence}%
            </div>
        </div>
        """

    @staticmethod
    def html(signal: dict) -> str:
        decision = signal.get("decision", "WAIT")
        confidence = signal.get("confidence", 0)
        trend = signal.get("trend", "Unknown")
        updated = signal.get("updated", "--")

        color = DashboardStyle.color(decision)

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
padding:25px;
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
text-align:center;
}}

.value {{
font-size:26px;
}}

</style>

</head>

<body>

<h1>🤖 GTI AI Dashboard</h1>

<div class="card">

<h2>Decision</h2>

<div class="decision">

{decision}

</div>

</div>

<div class="card">

<h2>Confidence</h2>

{DashboardStyle.progress(confidence)}

</div>

<div class="card">

<h2>Market Trend</h2>

<div class="value">

{trend}

</div>

</div>

<div class="card">

<h2>Updated</h2>

<div class="value">

{updated}

</div>

</div>

</body>

</html>
"""
