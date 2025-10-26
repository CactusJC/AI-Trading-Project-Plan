import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lnmarkets import rest

# API credentials sourced from environment variables for security
options = {
    'key': os.getenv('LNMARKETS_API_KEY'),
    'secret': os.getenv('LNMARKETS_API_SECRET'),
    'passphrase': os.getenv('LNMARKETS_API_PASSPHRASE'),
    'network': os.getenv('LNMARKETS_NETWORK', 'testnet')  # Default to testnet
}

def get_lnmarkets_client():
    """
    Initializes and returns the LN Markets REST client.
    """
    return rest.LNMarketsRest(**options)

if __name__ == '__main__':
    client = get_lnmarkets_client()
    try:
        user_str = client.get_user()
        user = json.loads(user_str)
        print("Successfully connected to LN Markets API.")
        print(f"User balance: {user['balance']} satoshis")
    except Exception as e:
        print(f"An error occurred: {e}")
