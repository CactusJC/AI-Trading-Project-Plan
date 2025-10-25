CREATE TABLE btc_daily_data (
    timestamp DATETIME PRIMARY KEY,
    market_price FLOAT,
    total_bitcoins BIGINT,
    market_cap FLOAT,
    trade_volume FLOAT,
    blocks_size INT,
    avg_block_size FLOAT,
    n_orphaned_blocks INT,
    n_transactions_per_block INT,
    median_confirmation_time FLOAT,
    hash_rate FLOAT,
    difficulty FLOAT,
    miners_revenue FLOAT,
    transaction_fees FLOAT,
    cost_per_transaction_percent FLOAT,
    cost_per_transaction FLOAT,
    n_unique_addresses INT,
    n_transactions INT,
    n_transactions_total BIGINT,
    n_transactions_excluding_popular INT,
    n_transactions_excluding_chains_longer_than_100 INT,
    output_volume FLOAT,
    estimated_transaction_volume FLOAT,
    estimated_transaction_volume_usd FLOAT
);

CREATE INDEX idx_timestamp ON btc_daily_data(timestamp);
