import numpy as np
import pandas as pd

def calculate_mvrv(df: pd.DataFrame, window: int = 365) -> pd.Series:
    """
    Calculates the Market Value to Realized Value (MVRV) ratio.
    This is a simplified version using historical price data as a proxy for realized value.
    """
    df['realized_value'] = df['market_price'].rolling(window=window).mean()
    df['mvrv'] = df['market_price'] / df['realized_value']
    return df['mvrv']

def calculate_sth_mvrv(df: pd.DataFrame, window: int = 155) -> pd.Series:
    """
    Calculates the Short-Term Holder MVRV (STH-MVRV) ratio.
    This is a simplified version using a shorter window to approximate short-term holder behavior.
    """
    df['sth_realized_value'] = df['market_price'].rolling(window=window).mean()
    df['sth_mvrv'] = df['market_price'] / df['sth_realized_value']
    return df['sth_mvrv']

def calculate_stock_to_flow(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the Stock-to-Flow ratio.
    This is a simplified model and requires assumptions about issuance.
    """
    # These are simplified assumptions for the purpose of this simulation
    initial_supply = 18_000_000  # Example starting supply
    halving_interval = 4 * 365  # Roughly 4 years in days
    initial_issuance = 50

    # Calculate daily issuance
    days_since_start = (df['timestamp'] - df['timestamp'].min()).dt.days
    halvings = (days_since_start // halving_interval).astype(int)
    daily_issuance = initial_issuance / (2 ** halvings)

    # Calculate total supply
    df['total_supply'] = initial_supply + daily_issuance.cumsum()
    df['annual_issuance'] = daily_issuance * 365

    # Calculate stock-to-flow
    df['stock_to_flow'] = df['total_supply'] / df['annual_issuance']
    return df['stock_to_flow']
