from flask import Flask, request, jsonify
import oandapyV20
import oandapyV20.endpoints.orders as orders

app = Flask(__name__)

# WARNING: Hardcoded credentials — use only for local/private testing
OANDA_API_KEY = "5b08908483e49919c3ef2483df9c2b9b-1cc7a7d4ffe75bb5fe3bb688d730462c"
ACCOUNT_ID = "101-002-30416430-003"

client = oandapyV20.API(access_token=OANDA_API_KEY)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    signal = data.get('message', '')

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
        return jsonify({"status": "Sell order sent"})

    return jsonify({"status": "Unknown signal"})