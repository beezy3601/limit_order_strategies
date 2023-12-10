from flask import Flask, request
import config
import requests
import json, hmac, hashlib, time
import http.client
from crypto import get_all_accounts
from price import get_crypto_price
from coinbase_advanced_trader.config import set_api_credentials
from coinbase_advanced_trader.strategies.limit_order_strategies import fiat_limit_buy, fiat_limit_sell, fiat_market_buy, fiat_market_sell
from decimal import Decimal, ROUND_DOWN

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
    ticker_quote = ticker[:-3]
   
    # ticker_symbol = f"{ticker[:3]}-{ticker[3:]}"

    accounts_data_response = get_all_accounts()

    if 'error' in accounts_data_response:
        return accounts_data_response['error']

    accounts_data = accounts_data_response.get('accounts', [])
    

# Print the available currencies in the account data for debugging
    available_currencies = [account['currency'] for account in accounts_data]

    



    # Extract USD balance
    ticker_balance = next((account['available_balance']['value'] for account in accounts_data if account['currency'] == ticker_quote), None)
    
    print(ticker_quote, ticker_balance)
    print(f"Available Currencies: {available_currencies}")
    
    if ticker_balance is None:
        return f"{ticker_quote} balance not found in account data."

    print(ticker_quote, ticker_balance)

    price = Decimal(get_crypto_price(ticker_symbol))

    # qty = ticker_balance[ticker_quote]['free']
    ticker_balance_mill = Decimal(ticker_balance)
    rounded_balance = ticker_balance_mill.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    print(rounded_balance)
    
    amount = (rounded_balance * price)/2

    # Place a market buy order
    sell_order_response = fiat_market_sell(ticker_symbol, amount)
    
    
    return {
        'sell_order': sell_order_response,
    }

if __name__ == '__main__':
    app.run(port=5000)  # Adjust the port and host as needed
