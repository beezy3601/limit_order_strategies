from flask import Flask, request
import requests
import config

import json, hmac, hashlib, time, requests
from requests.auth import AuthBase

app = Flask(__name__)


COINBASE_API_URL = "https://api.coinbase.com/v2"

def get_coinbase_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.API_KEY}",
    }

def get_all_markets():
    try:
        url = f"{COINBASE_API_URL}/products"
        response = requests.get(url, headers=get_coinbase_headers())
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        # Check if 'data' key is present in the response
        if 'data' not in data:
            return "Error fetching data from Coinbase API"

        return [product["id"] for product in data["data"]]
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

@app.route('/')
def index():
    # Get all markets and print them
    all_markets = get_all_markets()
    print("All Markets:", all_markets)

    return "Check the console for the list of markets."

# ... (rest of the code)

if __name__ == '__main__':
    app.run(port=5000)  # Adjust the port and host as needed
