import urllib.request


def send_ntfy_signal(
    symbol,
    action,
    entry=None,
    sl=None,
    tp=None,
    tf="",
    tp1=None,
    tp2=None,
    rr=None,
    confidence=None,
    bias=None,
    invalidation=None,
):
    topic = "gti_ai_geoffrey_signals"

    action = str(action).strip().upper()
    tf = str(tf).strip().upper()

    info_actions = {
        "START",
        "INFO",
        "STOP",
        "HEARTBEAT",
        "NO TRADE",
    }

    if action in info_actions:
        message = (
            f"ℹ️ GTI-AI-V2 SYSTEM STATUS\n"
            f"Asset: {symbol}\n"
            f"Status: {action}\n"
            f"Message: {entry}\n"
        )
        title = "GTI-AI-V2 SYSTEM STATUS"
        priority = "default"
    else:
        if tp1 is None:
            tp1 = tp

        message = (
            f"🚨 GTI-AI-V2 LIVE SIGNAL 🚨\n"
            f"Asset: {symbol} ({tf})\n"
            f"Action: {action}\n"
            f"Bias: {bias}\n"
            f"Confidence: {confidence}\n"
            f"Entry: {entry}\n"
            f"SL: {sl}\n"
            f"TP1: {tp1}\n"
            f"TP2: {tp2}\n"
            f"R:R: {rr}\n"
            f"Invalidation: {invalidation}\n"
            f"\n"
            f"👉 MANUAL EXECUTION: Weka order kwenye MT5."
        )
        title = f"GTI-AI-V2 LIVE SIGNAL: {action}"
        priority = "urgent"

    try:
        request = urllib.request.Request(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": priority,
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            response.read()

        print("ntfy notification imetumwa mafanikio!")

    except Exception as exc:
        print(
            f"ntfy notification error: "
            f"{type(exc).__name__}: {exc}"
        )
