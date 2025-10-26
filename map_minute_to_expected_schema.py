#!/usr/bin/env python3
# map_minute_to_expected_schema.py
import os
import numpy as np
import pandas as pd
import sqlite3

IN_CSV  = 'trading_ai_project/data/raw_csv/bitcoin_dataset_minute.csv'
OUT_CSV = 'trading_ai_project/data/raw_csv/bitcoin_dataset_mapped.csv'
OUT_DB  = 'trading_ai_project/database/trading_data_minute_mapped.db'
TABLE_NAME = 'btc_minute_mapped'

EXPECTED_COLS = [
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

def main():
    if not os.path.exists(IN_CSV):
        raise FileNotFoundError(f"Input CSV niet gevonden: {IN_CSV}")

    df = pd.read_csv(IN_CSV, parse_dates=['timestamp'])
    print("Input columns:", list(df.columns))

    out = pd.DataFrame(index=df.index, columns=EXPECTED_COLS)

    out['timestamp'] = df['timestamp']

    if 'close' in df.columns:
        out['market_price'] = pd.to_numeric(df['close'], errors='coerce')
    else:
        out['market_price'] = np.nan

    if 'volume' in df.columns:
        out['trade_volume'] = pd.to_numeric(df['volume'], errors='coerce')
        out['output_volume'] = out['trade_volume']
        out['estimated_transaction_volume'] = out['trade_volume']
    else:
        out['trade_volume'] = np.nan
        out['output_volume'] = np.nan
        out['estimated_transaction_volume'] = np.nan

    out['estimated_transaction_volume_usd'] = out['market_price'] * out['trade_volume']

    # Ensure all expected columns exist (explicit)
    for c in EXPECTED_COLS:
        if c not in out.columns:
            out[c] = np.nan

    out = out[EXPECTED_COLS]

    print("Filled counts per column:")
    print(out.notna().sum())

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    print(f"Mapped CSV saved: {OUT_CSV} (rows: {len(out)})")

    os.makedirs(os.path.dirname(OUT_DB), exist_ok=True)
    conn = sqlite3.connect(OUT_DB)
    out.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Mapped data written to SQLite DB: {OUT_DB}, table: {TABLE_NAME}")

if __name__ == '__main__':
    main()
