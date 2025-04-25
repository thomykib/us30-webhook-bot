from flask import Flask, request, jsonify
import oandapyV20
import oandapyV20.endpoints.orders as orders
import os
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

OANDA_API_KEY = os.environ.get("OANDA_API_KEY")
ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")
client = oandapyV20.API(access_token=OANDA_API_KEY)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Accept plain text body and parse manually
        raw_data = request.get_data(as_text=True)
        logging.info(f"Raw webhook received: {raw_data}")

        # Convert raw JSON string into a Python dict
        data = json.loads(raw_data)

        signal = data.get('message', '').upper()
        tp = data.get('tp')
        sl = data.get('sl')

        if signal in ['BUY_US30', 'SELL_US30']:
            units = "1" if signal == "BUY_US30" else "-1"
            order_data = {
                "order": {
                    "instrument": "US30_USD",
                    "units": units,
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
            }

            if tp:
                order_data["order"]["takeProfitOnFill"] = {"price": str(tp)}
            if sl:
                order_data["order"]["stopLossOnFill"] = {"price": str(sl)}

            r = orders.OrderCreate(ACCOUNT_ID, data=order_data)
            client.request(r)
            return jsonify({"status": f"{signal} order sent", "tp": tp, "sl": sl})

        return jsonify({"status": "Unknown signal"}), 400

    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
