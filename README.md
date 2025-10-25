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
trading_ai_project/
├── data/
│   └── raw_csv/
├── database/
│   └── sql_scripts/
├── env/
│   └── gym_env.py
├── models/
│   └── rl_agent.py
├── api/
│   └── lnmarkets_client.py
├── pine_scripts/
│   └── parser.py
├── notebooks/
│   └── analysis.ipynb
├── utils/
│   └── indicators.py
├── main.py
└── README.md
```

## Installation

### Prerequisites

-   Python 3.10+
-   TA-Lib

### 1. Install TA-Lib

TA-Lib is a C library, so it needs to be installed before the Python wrapper.

**On Linux (Ubuntu/Debian):**

```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
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

The project includes a script to download historical Bitcoin data and import it into a SQLite database.

```bash
# This step was already completed and the data is in the repository.
# To re-run the import, you can use the following script:
python3 trading_ai_project/utils/import_to_sqlite.py
```

### 2. Train the Agent

Train the reinforcement learning agent on the historical data.

```bash
python3 train_agent.py
```

This will save the trained model to `trading_ai_project/models/ppo_trading_agent.zip`.

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

### 5. Live Trading

Run the live trading simulation with the LN Markets API.

**Note:** You will need to configure your API keys in `trading_ai_project/api/lnmarkets_client.py`.

```python
# trading_ai_project/api/lnmarkets_client.py

options = {
    'key': 'YOUR_API_KEY',
    'secret': 'YOUR_API_SECRET',
    'passphrase': 'YOUR_API_PASSPHRASE',
    'network': 'testnet'  # Use 'mainnet' for real trading
}
```

Then, run the live trading script:

```bash
python3 live_trading.py
```

## Analysis

The `trading_ai_project/notebooks/analysis.ipynb` notebook provides a more in-depth analysis of the agent's performance.

## Pine Script Integration

The project includes an optional Pine Script parser that can be used to extract indicator information from TradingView Pine Scripts.

```bash
python3 trading_ai_project/pine_scripts/parser.py
```
