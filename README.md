# AI Trading Project

This project is a local AI application that predicts winning trades on historical and live Bitcoin data. It uses reinforcement learning to learn from the market and make trading decisions.

## Features

-   **Data-driven:** Learns from historical Bitcoin data.
-   **Reinforcement Learning:** Uses Stable-Baselines3 to train a PPO agent.
-   **Live Trading:** Integrates with the LN Markets API for live trading simulation.
-   **Technical Analysis:** Uses TA-Lib to incorporate technical indicators into the learning process.
-   **Extensible:** Includes an optional Pine Script parser to integrate with TradingView strategies.

## Project Structure

```
.
├── trading_ai_project/
│   ├── api/
│   ├── data/
│   ├── database/
│   ├── env/
│   ├── models/
│   ├── notebooks/
│   ├── pine_scripts/
│   └── utils/
├── backtest.py
├── evaluate_agent.py
├── inspect_client.py
├── install.sh
├── requirements.txt
├── setup.py
├── train_agent.py
├── verify_install.py
└── visualize_performance.py
```

## Installation

### Prerequisites

-   Python 3.10+
-   TA-Lib

### 1. Install TA-Lib

TA-Lib is a C library, so it needs to be installed before the Python wrapper.

**On Linux (Ubuntu/Debian):**

You can use the automated installation script to install all dependencies, including the TA-Lib C library.

```bash
chmod +x install.sh
./install.sh
```

**On macOS:**

```bash
brew install ta-lib
```

**On Windows:**

1.  Download the TA-Lib binary installer (`ta-lib-0.6.4-windows-x86_64.msi`) from the [official website](https://ta-lib.org/install/).
2.  Run the installer and follow the on-screen instructions.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the Project

Install the project in editable mode to make the `trading_ai_project` package available to the entire environment.

```bash
pip install -e .
```

## Usage

### 1. Download and Import Data

You can download fresh 1-minute Binance candles and map them to the expected schema.

```bash
# Fetch the last 30 days of BTC/USDT minute data (appends to existing CSV by default)
python3 fetch_binance_1m.py --days 30

# Map the raw CSV to the schema used by the rest of the project and load it into SQLite
python3 map_minute_to_expected_schema.py
```

> Tip: Use `--since 2024-01-01T00:00:00` or `--no-append` to control the exact date range you fetch.

### 2. Train the Agent

Train the reinforcement learning agent on the historical data.

```bash
python3 train_agent.py
```

This will save the trained model to `trading_ai_project/models/ppo_trading_agent.zip`.

To train directly on the 1-minute data you fetched and mapped, point the trainer to the minute database and table:

```bash
python3 train_agent.py \
  --db-path trading_ai_project/database/trading_data_minute_mapped.db \
  --table btc_minute_mapped \
  --timesteps 500000
```

### 3. Evaluate the Agent

Evaluate the trained agent's performance on the historical data.

```bash
python3 evaluate_agent.py
```

### 4. Visualize Performance

Generate a plot of the agent's performance.

```bash
python3 visualize_performance.py
```

This will save a `performance.png` file in the `trading_ai_project` directory.

### 5. Backtest with Random Actions

Run a simple backtest with random actions to see how the environment behaves.

```bash
python3 backtest.py
```

### 6. Inspect the LN Markets API Connection

Test the connection to the LN Markets API and inspect the client.

**Note:** You will need to configure your API keys as environment variables.

```bash
export LNMARKETS_API_KEY='YOUR_API_KEY'
export LNMARKETS_API_SECRET='YOUR_API_SECRET'
export LNMARKETS_API_PASSPHRASE='YOUR_API_PASSPHRASE'
export LNMARKETS_NETWORK='testnet'  # Use 'mainnet' for real trading
```

Then, run the inspection script:

```bash
python3 inspect_client.py
```

## Analysis

The `trading_ai_project/notebooks/analysis.ipynb` notebook provides a more in-depth analysis of the agent's performance.

## Pine Script Integration

The project includes an optional Pine Script parser that can be used to extract indicator information from TradingView Pine Scripts.

```bash
python3 trading_ai_project/pine_scripts/parser.py
```
