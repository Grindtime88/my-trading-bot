import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- SECURE CONFIGURATION ---
TL_URL = "https://live.tradelocker.com/backend-api"
EMAIL = os.environ.get("TL_EMAIL")
PASSWORD = os.environ.get("TL_PASSWORD")
SERVER = os.environ.get("TL_SERVER", "Funder Pro")
ACC_ID = os.environ.get("TL_ACC_ID")

def get_access_token():
    """Logs into TradeLocker to get a fresh JWT token."""
    auth_url = f"{TL_URL}/auth/jwt/token"
    payload = {"email": EMAIL, "password": PASSWORD, "server": SERVER}
    try:
        response = requests.post(auth_url, json=payload, timeout=10)
        return response.json().get("accessToken")
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return None

# --- HOME ROUTE (Visible Pings) ---
@app.route('/', methods=['GET'])
def home():
    print("🏠 Keep-alive ping received! Bot is awake.")
    return "Sniper Bot is Online", 200

# --- WEBHOOK ROUTE (Trade Execution) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data: return "No data", 400
    
    print(f"🎯 SIGNAL RECEIVED: {data['side']} {data['symbol']}")
    
    token = get_access_token()
    if not token: return "Auth Failed", 500

    order_url = f"{TL_URL}/trade/accounts/{ACC_ID}/orders"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    order_payload = {
        "qty": float(data['qty']),
        "side": data['side'].lower(),
        "symbol": data['symbol'],
        "type": "market",
        "stopLoss": float(data['sl']),
        "takeProfit": float(data['tp'])
    }

    try:
        resp = requests.post(order_url, json=order_payload, headers=headers)
        print(f"💰 TradeLocker Response: {resp.status_code} - {resp.text}")
        return "Order Processed", 200
    except Exception as e:
        print(f"❌ Execution Error: {e}")
        return "Order Failed", 500

if __name__ == "__main__":
    app.run()
