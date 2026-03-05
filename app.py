from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1. Receive data from TradingView
    data = request.json
    print(f"Signal Received: {data}")

    # 2. Extract info
    # Note: We'll add the TradeLocker connection logic once you confirm this works!
    symbol = data.get("symbol")
    side = data.get("side")
    
    return f"Bot received {side} for {symbol}", 200

if __name__ == "__main__":
    app.run()
