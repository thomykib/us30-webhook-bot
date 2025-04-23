from flask import Flask, request, jsonify
import oandapyV20
import oandapyV20.endpoints.orders as orders

app = Flask(__name__)

# WARNING: Use environment variables for production — these are hardcoded for demo
OANDA_API_KEY = "5b08908483e49919c3ef2483df9c2b9b-1cc7a7d4ffe75bb5fe3bb688d730462c"
ACCOUNT_ID = "101-002-30416430-003"

client = oandapyV20.API(access_token=OANDA_API_KEY)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Force JSON parsing to avoid 415 error
        data = request.get_json(force=True)
        print(f"🔔 Webhook received: {data}")
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400

    # Read message from TradingView alert payload
    signal = data.get('message', '').strip().upper()

    if signal == 'BUY_US30':
        order_data = {
            "order": {
                "instrument": "US30_USD",
                "units": "1",
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }
        r = orders.OrderCreate(ACCOUNT_ID, data=order_data)
        client.request(r)
        print("✅ Buy order sent to OANDA")
        return jsonify({"status": "Buy order sent"})

    elif signal == 'SELL_US30':
        order_data = {
            "order": {
                "instrument": "US30_USD",
                "units": "-1",
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }
        r = orders.OrderCreate(ACCOUNT_ID, data=order_data)
        client.request(r)
        print("✅ Sell order sent to OANDA")
        return jsonify({"status": "Sell order sent"})

    print("⚠️ Unknown or missing signal")
    return jsonify({"status": "Unknown signal"}), 400

# 🔌 Required for Render deployment
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
