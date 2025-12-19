import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from trading_ai_project.api.lnmarkets_client import get_lnmarkets_client

if __name__ == '__main__':
    # Check for required environment variables
    required_vars = ['LNMARKETS_API_KEY', 'LNMARKETS_API_SECRET', 'LNMARKETS_API_PASSPHRASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("Error: Missing environment variables for LN Markets API.")
        print(f"Please set the following variables: {', '.join(missing_vars)}")
        sys.exit(1)

    client = get_lnmarkets_client()
    try:
        user = client.get_user()
        print("Successfully connected to LN Markets API.")
        print("Raw user response:")
        print(user)
    except Exception as e:
        print(f"An error occurred: {e}")
