import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- SECURE CONFIGURATION ---
# These pull from the "Environment" tab you set up in Render
TL_URL   = "https://demo.tradelocker.com/backend-api"
EMAIL    = os.environ.get("TL_EMAIL")
PASSWORD = os.environ.get("TL_PASSWORD")
SERVER   = os.environ.get("TL_SERVER", "Funder Pro")
ACC_ID   = os.environ.get("TL_ACC_ID")

def get_access_token():
    """Authenticates with TradeLocker to get a fresh JWT token."""
    auth_url = f"{TL_URL}/auth/jwt/token"
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "server": SERVER
    }
    try:
        # Use a timeout so the bot doesn't hang if the API is slow
        response = requests.post(auth_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("accessToken")
    except Exception as e:
        print(f"❌ AUTH ERROR: {e}")
        return None

# --- HOME ROUTE (Keeps the bot awake) ---
@app.route('/', methods=['GET'])
def home():
    print("🏠 Keep-alive ping received! Bot is awake.")
    return "Inducement Sniper is Online", 200

# --- WEBHOOK ROUTE (Receives TradingView Alerts) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        print("⚠️ Received empty request")
        return "No data", 400
    
    # Log the incoming signal for debugging
    print(f"🎯 SIGNAL RECEIVED: {data.get('side')} {data.get('symbol')}")
    
    # 1. Get a fresh token for this trade
    token = get_access_token()
    if not token:
        return "Auth Failed", 500

    # 2. Build the order request
    order_url = f"{TL_URL}/trade/accounts/{ACC_ID}/orders"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    # Formatting data correctly for TradeLocker
    order_payload = {
        "qty": float(data['qty']),
        "side": data['side'].lower(), # Ensures 'buy' or 'sell'
        "symbol": data['symbol'],
        "type": "market",
        "stopLoss": float(data['sl']),
        "takeProfit": float(data['tp'])
    }

    # 3. Send the order to the broker
    try:
        resp = requests.post(order_url, json=order_payload, headers=headers, timeout=10)
        print(f"💰 TRADELOCKER RESPONSE: {resp.status_code} - {resp.text}")
        return "Order Processed", 200
    except Exception as e:
        print(f"❌ EXECUTION ERROR: {e}")
        return "Order Failed", 500

# --- STARTUP LOGIC ---
if __name__ == "__main__":
    # Render uses the 'PORT' environment variable to tell us where to listen
    port = int(os.environ.get("PORT", 5000))
    # '0.0.0.0' is required for the app to be reachable from the internet
    app.run(host='0.0.0.0', port=port)
