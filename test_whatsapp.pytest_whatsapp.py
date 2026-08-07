import requests
import urllib.parse

# Weka namba yako ya simu na API Key hapa
PHONE_NUMBER = "+255XXXXXXXXX"  # Weka namba yako ya WhatsApp kwa umbizo la kimataifa (mfano: +255712345678)
API_KEY = "WEKA_API_KEY_YAKO_HAPA"  # Weka API Key uliyopokea kutoka CallMeBot

def send_whatsapp_test():
    message = (
        "🤖 *GTI-AI-V2 LIVE DEMO TEST*\n\n"
        "📊 *Symbol:* XAUUSD (Gold)\n"
        "📈 *Action:* BUY\n"
        "💵 *Entry Price:* 2400.00\n"
        "🛑 *Stop Loss:* 2390.00\n"
        "🎯 *Take Profit:* 2420.00\n\n"
        "✅ *Status:* Connection Successful!"
    )
    
    # Kuingiza text kwenye URL format
    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded_message}&apikey={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        print(" Ujumbe umetumwa kikamilifu kwenye WhatsApp Business yako!")
    else:
        print(f"❌ Imefeli: {response.text}")

if __name__ == "__main__":
    send_whatsapp_test()

import requests
import urllib.parse

# Weka namba yako ya simu na API Key kutoka CallMeBot
PHONE_NUMBER = "+255XXXXXXXXX"  # Badilisha na namba yako ya WhatsApp (mfano: +255712345678)
API_KEY = "WEKA_API_KEY_HAPA"   # Badilisha na API Key uliyopata kutoka CallMeBot

def send_whatsapp_test():
    message = (
        "🤖 *GTI-AI-V2 LIVE DEMO TEST*\n\n"
        "📊 *Symbol:* XAUUSD (Gold)\n"
        "📈 *Action:* BUY\n"
        "💵 *Entry Price:* 2400.00\n"
        "🛑 *Stop Loss:* 2390.00\n"
        "🎯 *Take Profit:* 2420.00\n\n"
        "✅ *Status:* Connection Successful!"
    )

    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded_message}&apikey={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("Ujumbe umetumwa kikamilifu kwenye WhatsApp Business yako!")
        else:
            print(f"Imefeli: {response.text}")
    except Exception as e:
        print(f"Hitilafu kwenye mtandao: {e}")

if __name__ == "__main__":
    send_whatsapp_test()

cd ~/GTI-AI-V2
cat << 'EOF' > test_whatsapp.py
import requests
import urllib.parse

PHONE_NUMBER = "+255754203511"
API_KEY = "API_KEY_YAKO_HAPA"  # Weka API Key ya CallMeBot hapa

def send_whatsapp_test():
    message = (
        "🤖 *GTI-AI-V2 LIVE DEMO TEST*\n\n"
        "📊 *Symbol:* XAUUSD (Gold)\n"
        "📈 *Action:* BUY\n"
        "💵 *Entry Price:* 2400.00\n"
        "🛑 *Stop Loss:* 2390.00\n"
        "🎯 *Take Profit:* 2420.00\n\n"
        "✅ *Status:* Connection Successful!"
    )

    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded_message}&apikey={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(" Ujumbe umetumwa kikamilifu kwenye WhatsApp (+255754203511)!")
        else:
            print(f" Imefeli: {response.text}")
    except Exception as e:
        print(f" Hitilafu ya mtandao: {e}")

if __name__ == "__main__":
    send_whatsapp_test()
EOF

cd ~/GTI-AI-V2
cat << 'EOF' > test_whatsapp.py
import requests
import urllib.parse

PHONE_NUMBER = "+255754203511"
API_KEY = "API_KEY_YAKO_HAPA"  # Weka API Key ya CallMeBot hapa

def send_whatsapp_test():
    message = (
        "🤖 *GTI-AI-V2 LIVE DEMO TEST*\n\n"
        "📊 *Symbol:* XAUUSD (Gold)\n"
        "📈 *Action:* BUY\n"
        "💵 *Entry Price:* 2400.00\n"
        "🛑 *Stop Loss:* 2390.00\n"
        "🎯 *Take Profit:* 2420.00\n\n"
        "✅ *Status:* Connection Successful!"
    )

    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded_message}&apikey={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(" Ujumbe umetumwa kikamilifu kwenye WhatsApp (+255754203511)!")
        else:
            print(f" Imefeli: {response.text}")
    except Exception as e:
        print(f" Hitilafu ya mtandao: {e}")

if __name__ == "__main__":
    send_whatsapp_test()
EOF


cd ~/GTI-AI-V2
cat << 'EOF' > test_whatsapp.py
import requests
import urllib.parse

PHONE_NUMBER = "+255754203511"
API_KEY = "API_KEY_YAKO_HAPA"  # Weka API Key ya CallMeBot hapa

def send_whatsapp_test():
    message = (
        "🤖 *GTI-AI-V2 LIVE DEMO TEST*\n\n"
        "📊 *Symbol:* XAUUSD (Gold)\n"
        "📈 *Action:* BUY\n"
        "💵 *Entry Price:* 2400.00\n"
        "🛑 *Stop Loss:* 2390.00\n"
        "🎯 *Take Profit:* 2420.00\n\n"
        "✅ *Status:* Connection Successful!"
    )

    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded_message}&apikey={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(" Ujumbe umetumwa kikamilifu kwenye WhatsApp (+255754203511)!")
        else:
            print(f" Imefeli: {response.text}")
    except Exception as e:
        print(f" Hitilafu ya mtandao: {e}")

if __name__ == "__main__":
    send_whatsapp_test()
EOF

python test_whatsapp.py


