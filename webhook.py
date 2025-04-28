from flask import Flask, request, jsonify
import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import os
import json
import logging

# === Flask App ===
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# === OANDA Credentials ===
OANDA_API_KEY = os.environ.get("OANDA_API_KEY")
ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")
client = oandapyV20.API(access_token=OANDA_API_KEY)

# === Health Check Route ===
@app.route('/', methods=['GET'])
def home():
    return "Webhook server is running!", 200

# === Webhook Receive Route ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        raw_data = request.get_data(as_text=True)
        logging.info(f"Webhook hit. Raw data: {raw_data}")

        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON payload: {e}")
            return jsonify({"error": "Invalid JSON payload"}), 400

        signal = data.get('message', '').upper()
        logging.info(f"Signal parsed: {signal}")

        # === Handle Trade Commands ===
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
            logging.info(f"OANDA Buy Order placed: {order_data}")
            return jsonify({"status": "BUY_US30 order executed"}), 200

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
            logging.info(f"OANDA Sell Order placed: {order_data}")
            return jsonify({"status": "SELL_US30 order executed"}), 200

        elif signal == 'EXIT_US30':
            # === Proper OANDA trade close ===
            open_trades = trades.OpenTrades(ACCOUNT_ID)
            client.request(open_trades)
            trades_data = open_trades.response.get('trades', [])

            us30_trade = None
            for t in trades_data:
                if t['instrument'] == 'US30_USD':
                    us30_trade = t
                    break

            if us30_trade:
                trade_id = us30_trade['id']
                close_trade = trades.TradeClose(ACCOUNT_ID, tradeID=trade_id)
                client.request(close_trade)
                logging.info(f"Closed US30 trade ID {trade_id}")
                return jsonify({"status": "US30 trade closed"}), 200
            else:
                logging.warning("No open US30 trades found.")
                return jsonify({"status": "No open US30 trades found"}), 200

        else:
            logging.warning(f"Unknown signal received: {signal}")
            return jsonify({"error": "Unknown signal"}), 400

    except Exception as e:
        logging.error(f"General webhook error: {e}")
        return jsonify({"error": str(e)}), 500

# === Run Server ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
