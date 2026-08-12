import urllib.request

def send_ntfy_signal(symbol, action, entry, sl, tp, tf):
    topic = "gti_ai_geoffrey_signals"
    message = (
        f"🚨 GTI-AI-V2 LIVE SIGNAL 🚨\n"
        f"Asset: {symbol} ({tf})\n"
        f"Action: {action}\n"
        f"Entry: {entry}\n"
        f"SL: {sl} | TP: {tp}\n"
        f"👉 Weka Order Manual kwenye MT5 Sasa!"
    )

    url = f"https://ntfy.sh/{topic}"
    data = message.encode("utf-8")

    req = urllib.request.Request(url, data=data, headers={
        "Title": f"MT5 Signal: {action} {symbol}",
        "Priority": "urgent",
        "Tags": "rotating_light,chart_with_upwards_trend"
    })

    try:
        with urllib.request.urlopen(req) as response:
            print("Signal imetumwa kwenye ntfy mafanikio!")
    except Exception as e:
        print(f"Hitilafu ya kutuma ntfy: {e}")
