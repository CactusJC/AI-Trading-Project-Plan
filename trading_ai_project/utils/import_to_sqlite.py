import sqlite3
import pandas as pd

def import_data_to_sqlite(csv_filepath, db_filepath, table_name):
    """
    Imports data from a CSV file into a SQLite database.

    Args:
        csv_filepath (str): The path to the CSV file.
        db_filepath (str): The path to the SQLite database file.
        table_name (str): The name of the table to create.
    """
    # Load the data from the CSV file
    df = pd.read_csv(csv_filepath)

    # Clean up column names to match the database schema
    df.columns = [
        'timestamp', 'market_price', 'total_bitcoins', 'market_cap',
        'trade_volume', 'blocks_size', 'avg_block_size', 'n_orphaned_blocks',
        'n_transactions_per_block', 'median_confirmation_time', 'hash_rate',
        'difficulty', 'miners_revenue', 'transaction_fees',
        'cost_per_transaction_percent', 'cost_per_transaction',
        'n_unique_addresses', 'n_transactions', 'n_transactions_total',
        'n_transactions_excluding_popular',
        'n_transactions_excluding_chains_longer_than_100', 'output_volume',
        'estimated_transaction_volume', 'estimated_transaction_volume_usd'
    ]

    # Convert the 'timestamp' column to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_filepath)

    # Write the data to the SQLite database
    df.to_sql(table_name, conn, if_exists='replace', index=False)

    # Close the connection
    conn.close()

if __name__ == '__main__':
    import_data_to_sqlite(
        'trading_ai_project/data/raw_csv/bitcoin_dataset.csv',
        'trading_ai_project/database/trading_data.db',
        'btc_daily_data'
    )
    print("Data imported successfully to trading_data.db")
