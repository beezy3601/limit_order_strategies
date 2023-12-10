import http.client
import json
import config
import hmac
import hashlib
import time

class CoinbaseWalletAuth:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.timestamp = str(int(time.time()))

    def generate_signature(self, method, path, body=''):
        message = f"{self.timestamp}{method}{path}{body}"
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return signature

    def get_headers(self, method, path, body=''):
        return {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': self.generate_signature(method, path, body),
            'CB-ACCESS-TIMESTAMP': self.timestamp,
            'Content-Type': 'application/json',
        }

def get_crypto_price(ticker_symbol):
    url = f"/api/v3/brokerage/products/{ticker_symbol}/ticker"

    # Replace YOUR_API_KEY and YOUR_SECRET_KEY with your actual Coinbase API key and secret
    auth = CoinbaseWalletAuth(config.API_KEY, config.SECRET_KEY)
    
    connection = http.client.HTTPSConnection("api.coinbase.com")
    connection.request("GET", url, headers=auth.get_headers("GET", url))
    response = connection.getresponse()

    if response.status != 200:
        print(f"Error retrieving crypto price: {response.status}")
        return {'error': f"Error retrieving crypto price: {response.status}"}

    data = json.loads(response.read().decode("utf-8"))
    
    # Extract and return only the price from the first trade
    price = data.get('trades', [])[0].get('price') if data.get('trades') else None
    
    return price

# Example usage:
if __name__ == "__main__":
    ticker_symbol = "BTC-USDC"
    last_price = get_crypto_price(ticker_symbol)

    print("Last Price:", last_price)
