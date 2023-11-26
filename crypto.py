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

def get_all_accounts():
    url = "/api/v3/brokerage/accounts"
    limit = 250
    cursor = None

    auth = CoinbaseWalletAuth(config.API_KEY, config.SECRET_KEY)
    
    accounts_data = []

    while True:
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor

        connection = http.client.HTTPSConnection("api.coinbase.com")
        connection.request("GET", f"{url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}", headers=auth.get_headers("GET", url))
        response = connection.getresponse()

        if response.status != 200:
            print(f"Error retrieving accounts: {response.status}")
            return {'error': f"Error retrieving accounts: {response.status}"}

        data = json.loads(response.read().decode("utf-8"))

        for account in data.get("accounts", []):
            print(f"{account['currency']} Balance: {account['available_balance']['value']} {account['available_balance']['currency']}")
            accounts_data.append(account)

        if 'has_next' in data and data['has_next']:
            cursor = data['cursor']
        else:
            break

    connection.close()
    return {'accounts': accounts_data}


if __name__ == "__main__":
    get_all_accounts()
