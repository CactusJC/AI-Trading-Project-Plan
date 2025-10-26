#!/usr/bin/env python3
# fetch_binance_1m.py - download 1m OHLCV candles for BTC/USDT and save CSV
import ccxt, time, pandas as pd, os
from datetime import datetime, timezone

def fetch_ohlcv_binance(symbol='BTC/USDT', timeframe='1m',
                        since_dt=None, until_dt=None,
                        limit=1000, out_csv='trading_ai_project/data/raw_csv/bitcoin_dataset_minute.csv'):
    ex = ccxt.binance({'enableRateLimit': True})
    if since_dt is None:
        since_ms = int((datetime.now(timezone.utc) - pd.Timedelta(days=7)).timestamp() * 1000)
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

if __name__ == '__main__':
    # default: laatste 7 dagen
    fetch_ohlcv_binance()
