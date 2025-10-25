import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from trading_ai_project.api.lnmarkets_client import get_lnmarkets_client

if __name__ == '__main__':
    client = get_lnmarkets_client()
    try:
        user = client.get_user()
        print("Successfully connected to LN Markets API.")
        print("Raw user response:")
        print(user)
    except Exception as e:
        print(f"An error occurred: {e}")
