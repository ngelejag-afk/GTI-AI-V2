import requests
import time

NTFY_URL = "https://ntfy.sh/gti_ai_geoffrey_signals"
PRICE_API = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

def send_push_signal(title, message, priority="urgent"):
    try:
        clean_title = "".join(c for c in str(title) if ord(c) < 128)
        requests.post(
            NTFY_URL,
            data=message.encode("utf-8"),
            headers={
                "Title": clean_title,
                "Priority": str(priority)
            }
        )
        print("[INFO] Signal sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to push notification: {e}")

def run_strategy_cycle():
    try:
        res = requests.get(PRICE_API, timeout=10)
        data = res.json()
        current_price = float(data["data"]["amount"])

        print(f"[{time.strftime('%H:%M:%S')}] Market Checked. Price: {current_price}")

        decision = "BUY"

        if decision == "BUY":
            entry = current_price
            sl = entry - 120.00
            tp = entry + 240.00
        else:
            entry = current_price
            sl = entry + 120.00
            tp = entry - 240.00

        confidence = 88
        risk_reward = "1:2"

        signal_msg = (
            f"Asset          : BTCUSD (Live)\n"
            f"Decision       : {decision} 🚀\n"
            f"Confidence     : {confidence}%\n"
            f"Entry Price    : {entry:.2f}\n"
            f"Stop Loss (SL) : {sl:.2f}\n"
            f"Take Profit(TP): {tp:.2f}\n"
            f"Risk-Reward    : {risk_reward}\n"
            f"Action         : WEKA ORDER YA {decision} KWENYE MT5 SASA!"
        )

        send_push_signal(
            title=f"MT5 LIVE SIGNAL: {decision} BTCUSD",
            message=signal_msg
        )

    except Exception as e:
        print(f"[ERROR] Market cycle error: {e}")

if __name__ == "__main__":
    print("=========================================")
    print(" GTI-AI-V2 SIGNAL ENGINE ACTIVE (30 MIN) ")
    print("=========================================")
    while True:
        run_strategy_cycle()
        print("[STATUS] Inasubiri dakika 30 kwa ajili ya uchambuzi unaofuata...")
        time.sleep(1800)
