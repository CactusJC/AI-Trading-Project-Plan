#!/usr/bin/env python3
"""fetch_binance_1m.py

Download 1 minute OHLCV candles from Binance and store them to CSV. The script
is resilient to API hiccups, can append to existing datasets, and lets you
control the amount of history that is pulled.
"""

import argparse
import os
import time
from datetime import datetime, timezone

import ccxt
import pandas as pd

def fetch_ohlcv_binance(symbol: str = "BTC/USDT",
                        timeframe: str = "1m",
                        since_dt: datetime | None = None,
                        until_dt: datetime | None = None,
                        limit: int = 1000,
                        out_csv: str = "trading_ai_project/data/raw_csv/bitcoin_dataset_minute.csv",
                        days: int = 30,
                        append: bool = True):
    """Fetch OHLCV data from Binance.

    Args:
        symbol: Trading pair to download.
        timeframe: Candle timeframe.
        since_dt: Optional start datetime (UTC aware or naive treated as UTC).
        until_dt: Optional end datetime.
        limit: API page size.
        out_csv: Target CSV path.
        days: Amount of history to fetch if ``since_dt`` is not provided.
        append: If True, continue from the last timestamp in ``out_csv`` when it exists.
    """

    ex = ccxt.binance({"enableRateLimit": True})

    if append and os.path.exists(out_csv):
        try:
            existing = pd.read_csv(out_csv, parse_dates=["timestamp"])
            if not existing.empty:
                since_dt = existing["timestamp"].max().to_pydatetime()
                print(f"Continuing from last timestamp in existing CSV: {since_dt}")
        except Exception as exc:  # pragma: no cover - defensive read
            print(f"Could not read existing CSV, starting fresh. Reason: {exc}")

    if since_dt is None:
        since_ms = int((datetime.now(timezone.utc) - pd.Timedelta(days=days)).timestamp() * 1000)
    else:
        since_ms = int(since_dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
    until_ms = None
    if until_dt is not None:
        until_ms = int(until_dt.replace(tzinfo=timezone.utc).timestamp() * 1000)

    all_rows = []
    retry = 0
    while True:
        try:
            ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=limit)
        except Exception as e:
            retry += 1
            if retry > 8:
                raise
            print(f"API error, retry {retry}: {e}. sleeping 5s")
            time.sleep(5)
            continue

        if not ohlcv:
            break

        all_rows.extend(ohlcv)
        last_ts = ohlcv[-1][0]
        since_ms = last_ts + 1

        if until_ms and last_ts >= until_ms:
            break

        if len(ohlcv) < limit:
            break

        time.sleep(ex.rateLimit / 1000.0)

    df = pd.DataFrame(all_rows, columns=['ts_ms','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['ts_ms'], unit='ms', utc=True)
    df = df[['timestamp','open','high','low','close','volume']]
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Saved {len(df)} rows to {out_csv}")
    return out_csv

def _parse_dt(dt_str: str | None):
    if dt_str is None:
        return None
    return datetime.fromisoformat(dt_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download Binance 1m OHLCV data to CSV")
    parser.add_argument("--symbol", default="BTC/USDT", help="Trading pair to fetch (default: BTC/USDT)")
    parser.add_argument("--timeframe", default="1m", help="Candle timeframe (default: 1m)")
    parser.add_argument("--days", type=int, default=30, help="History (in days) to fetch when no --since is provided")
    parser.add_argument("--since", help="ISO timestamp to start from (UTC)")
    parser.add_argument("--until", help="ISO timestamp to stop at (UTC)")
    parser.add_argument("--limit", type=int, default=1000, help="Page size for API calls")
    parser.add_argument("--out-csv", default="trading_ai_project/data/raw_csv/bitcoin_dataset_minute.csv",
                        help="Destination CSV path")
    parser.add_argument("--no-append", action="store_true", help="Do not append/continue from existing CSV")

    args = parser.parse_args()

    fetch_ohlcv_binance(
        symbol=args.symbol,
        timeframe=args.timeframe,
        since_dt=_parse_dt(args.since),
        until_dt=_parse_dt(args.until),
        limit=args.limit,
        out_csv=args.out_csv,
        days=args.days,
        append=not args.no_append,
    )
