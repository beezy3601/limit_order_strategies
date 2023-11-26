from flask import Flask, request
import config
import requests
import json, hmac, hashlib, time
import http.client
from crypto import get_all_accounts
from price import get_crypto_price
from coinbase_advanced_trader.config import set_api_credentials
from coinbase_advanced_trader.strategies.limit_order_strategies import fiat_limit_buy, fiat_limit_sell, fiat_market_buy

API_KEY = config.API_KEY
API_SECRET = config.SECRET_KEY


set_api_credentials(API_KEY, API_SECRET)

class CoinbaseWalletAuth:

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.timestamp = str(int(time.time()))

    def __call__(self, method, url, body=None):
        message = self.timestamp + method + url + (body or '')
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        auth = CoinbaseWalletAuth(config.API_KEY, config.SECRET_KEY)
        headers = {
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': self.timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'Content-Type': 'application/json',  # Add this line for Content-Type
        }

        return headers

app = Flask(__name__)

COINBASE_API_URL = "https://api.coinbase.com/api/v3/brokerage"


@app.route('/trading-webhook', methods=['POST'])
def trading_webhook():
    data = request.json
    

    if __name__ == "__main__":
        get_all_accounts()

    # Extract relevant information from TradingView alert payload
    ticker = data['ticker']
    ticker_symbol = ticker[:-3] + '-USD'
   
    # ticker_symbol = f"{ticker[:3]}-{ticker[3:]}"

    accounts_data_response = get_all_accounts()

    if 'error' in accounts_data_response:
        return accounts_data_response['error']

    accounts_data = accounts_data_response.get('accounts', [])

    # Extract USD balance
    usd_balance = next((account['available_balance']['value'] for account in accounts_data if account['currency'] == 'USD'), None)

    if usd_balance is None:
        return "USD balance not found in account data."

    price = float(get_crypto_price(ticker_symbol))

    dry_powder = float(usd_balance)
    
    if dry_powder < 200:
        qty = dry_powder / price
    else:
        qty = dry_powder * 0.17 / price

    if qty <= 0:
        return "Insufficient quantity."
    
    amount = (qty * price)

    # Place a market buy order
    buy_order_response = fiat_market_buy(ticker_symbol, amount)
    
    # Calculate take profit price
    # take_profit_price = price * 1.0175  # Set take profit 1% higher than buy price
    sell_qty = qty * 0.32

    # Place a limit sell order with take profit
    take_profit_order_response = fiat_limit_sell(ticker_symbol, sell_qty, 1.0175)
    
    return {
        'buy_order': buy_order_response,
        'take_profit_order': take_profit_order_response
    }

if __name__ == '__main__':
    app.run(port=5000)  # Adjust the port and host as needed
