import pandas as pd

def load_bitcoin_data(filepath):
    """
    Loads bitcoin data from a CSV file.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        pandas.DataFrame: The loaded data.
    """
    return pd.read_csv(filepath)

if __name__ == '__main__':
    data = load_bitcoin_data('trading_ai_project/data/raw_csv/bitcoin_dataset.csv')
    print(data.head())
