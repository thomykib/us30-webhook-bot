from flask import Flask, request, jsonify
import oandapyV20
import oandapyV20.endpoints.orders as orders
import logging

app = Flask(__name__)
OANDA_API_KEY = "5b08908483e49919c3ef2483df9c2b9b-1cc7a7d4ffe75bb5fe3bb688d730462c"
ACCOUNT_ID = "101-002-30416430-003"
client = oandapyV20.API(access_token=OANDA_API_KEY)

logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logging.info(f"Received webhook: {data}")
        signal = data.get('message', '')

        if signal == 'buy_US30':
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
            return jsonify({"status": "Buy order sent"})

        elif signal == 'sell_US30':
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
            return jsonify({"status": "Sell order sent"})

        elif signal == 'exit_US30':
            order_data = {
                "order": {
                    "instrument": "US30_USD",
                    "units": "0",
                    "type": "MARKET",
                    "positionFill": "CLOSE"
                }
            }
            r = orders.OrderCreate(ACCOUNT_ID, data=order_data)
            client.request(r)
            return jsonify({"status": "Exit order sent"})

        return jsonify({"status": "Unknown signal"})

    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
