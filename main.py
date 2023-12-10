import json, hmac, hashlib, time, requests
from requests.auth import AuthBase
import config
from coinbase_advanced_trader.strategies.limit_order_strategies import fiat_limit_sell

# Before implementation, set environmental variables with the names API_KEY and API_SECRET
API_KEY = config.API_KEY
API_SECRET = config.SECRET_KEY

# Create custom authentication for Coinbase API
class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.timestamp = str(int(time.time()))  # Move the timestamp definition here

    def __call__(self, request):
        message = self.timestamp + request.method + request.path_url + (request.body or '')
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': self.timestamp,  # Use self.timestamp here
            'CB-ACCESS-KEY': self.api_key,
        })
        return request

api_url = 'https://api.coinbase.com/v2/'
auth = CoinbaseWalletAuth(API_KEY, API_SECRET)

# Get current user
r = requests.get(api_url + 'user', auth=auth)
print(r.json())

print("Request Headers:", r.request.headers)
print(f"API Key: {API_KEY}")
print(f"Secret Key: {API_SECRET}")
print(f"Timestamp: {auth.timestamp}")  # Access timestamp using auth.timestamp
