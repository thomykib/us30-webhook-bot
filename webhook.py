from flask import Flask, request, jsonify
import oandapyV20
import oandapyV20.endpoints.orders as orders
import os
import json
import logging

# === Flask App ===
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# === OANDA Credentials ===
OANDA_API_KEY = os.environ.get("OANDA_API_KEY")
ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")

# === OANDA API Client ===
client = oandapyV20.API(access_token=OANDA_API_KEY)

# === Health Check Route ===
@app.route('/', methods=['GET'])
def home():
    return "Webhook server is running!", 200

# === Webhook Receive Route ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Log raw incoming data
        raw_data = request.get_data(as_text=True)
        logging.info(f"Webhook hit. Raw data: {raw_data}")

        # Parse JSON safely
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON payload: {e}")
            return jsonify({"error": "Invalid JSON payload"}), 400

        signal = data.get('message', '').upper()
        logging.info(f"Signal parsed: {signal}")

        # Build order depending on signal
        if signal == 'BUY_US30':
            order_data = {
                "order": {
                    "instrument": "US30_USD",
                    "units": "1",
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
            }
        elif signal == 'SELL_US30':
            order_data = {
                "order": {
                    "instrument": "US30_USD",
                    "units": "-1",
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
            }
        elif signal == 'EXIT_US30':
            order_data = {
                "order": {
                    "instrument": "US30_USD",
                    "units": "0",
                    "type": "MARKET",
                    "positionFill": "CLOSE"
                }
            }
        else:
            logging.warning(f"Unknown signal received: {signal}")
            return jsonify({"error": "Unknown signal received"}), 400

        # Send the order to OANDA
        try:
            r = orders.OrderCreate(ACCOUNT_ID, data=order_data)
            client.request(r)
            logging.info(f"OANDA order placed: {order_data}")
            return jsonify({"status": f"{signal} order successfully sent"}), 200
        except Exception as e:
            logging.error(f"Error sending order to OANDA: {e}")
            return jsonify({"error": f"Failed to send order to OANDA: {str(e)}"}), 500

    except Exception as e:
        logging.error(f"General webhook error: {e}")
        return jsonify({"error": str(e)}), 500

# === Run Server ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
