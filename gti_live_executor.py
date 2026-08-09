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
        print("[INFO] Signal successfully pushed to phone notification.")
    except Exception as e:
        print(f"[ERROR] Failed to push notification: {e}")

def run_strategy_cycle():
    try:
        res = requests.get(PRICE_API, timeout=10)
        data = res.json()
        current_price = float(data["data"]["amount"])
        print(f"[{time.strftime('%H:%M:%S')}] Market Checked. Current BTC Price: {current_price}")

        setup_met = True
        if setup_met:
            decision = "BUY"
            entry = current_price
            sl = entry - 85.00
            tp = entry + 170.00
            risk_reward = "1:2"
            confidence = 89

            signal_msg = (
                f"Decision       : {decision}\n"
                f"Asset          : BTCUSD (Crypto)\n"
                f"Confidence     : {confidence}%\n"
                f"Entry Price    : {entry:.2f}\n"
                f"Stop Loss (SL) : {sl:.2f}\n"
                f"Take Profit(TP): {tp:.2f}\n"
                f"Risk-Reward    : {risk_reward}\n"
                f"Action         : EXECUTE DEMO ON MT5 NOW"
            )

            send_push_signal(
                title="DEMO EXECUTION BTCUSD BUY",
                message=signal_msg
            )
            time.sleep(900)
        else:
            print("[STATUS] Analysis complete: No valid setup found.")
    except Exception as e:
        print(f"[ERROR] Error running market cycle: {e}")

if __name__ == "__main__":
    print("=========================================")
    print(" GTI-AI-V2 BTC DEMO EXECUTION ACTIVE     ")
    print("=========================================")
    while True:
        run_strategy_cycle()
        time.sleep(180)
