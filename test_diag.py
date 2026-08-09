import requests

print("Running GTI-AI-V2 diagnostic...")

# Test ntfy.sh webhook notification
try:
    res = requests.post(
        "https://ntfy.sh/gti_ai_geoffrey_signals",
        data="Diagnostic test from GTI-AI-V2 script!".encode("utf-8"),
        headers={
            "Title": "GTI-AI Diagnostic",
            "Priority": "high",
            "Tags": "moneybag,chart_with_upwards_trend"
        }
    )
    if res.status_code == 200:
        print("Ntfy notification sent successfully! Check your phone.")
    else:
        print(f"Ntfy failed with status code: {res.status_code}")
except Exception as e:
    print(f"Ntfy connection error: {e}")

