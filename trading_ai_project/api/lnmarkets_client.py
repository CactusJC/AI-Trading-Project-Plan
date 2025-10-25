import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lnmarkets import rest

# Replace with your actual API keys
options = {
    'key': 'Zai8xehXFyl0JbIEBTGmP9cZ4knExRdbfb8Ki24ukR4=',
    'secret': 'N4tvsDZtpevqeWuQ1dJ2MpK6SGlJh0Ocm43kB3yHbF9agQkP0JURO8zA0U9DiUyGzQFAFYMGSOcYtEPli8mTJA==',
    'passphrase': '557569edb3fai',
    'network': 'testnet'  # Use 'mainnet' for real trading
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
