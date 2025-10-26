#!/usr/bin/env python3
"""
AI Trading Agent Trainer Script
--------------------------------
This script trains a PPO trading agent using the configured environment.
It is designed for use by higher-level AI agents or automated pipelines.

Features:
- Loads configuration from YAML.
- Validates training data presence in SQLite database.
- Creates a vectorized Gym environment (Stable-Baselines3 compatible).
- Logs training progress to TensorBoard.
- Saves trained model to disk.
"""

import os
import yaml
import sqlite3
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from trading_ai_project.env.gym_env import TradingEnv


def verify_training_data(db_path, table_name="btc_daily_data", min_rows=100):
    """
    Checks if training data exists and meets a minimum row requirement.

    Args:
        db_path (str): Path to SQLite database file.
        table_name (str): Name of the table to check.
        min_rows (int): Minimum number of rows required to proceed.

    Returns:
        bool: True if valid data found, False otherwise.
    """
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql(f"SELECT COUNT(*) AS rows FROM {table_name}", conn)
        rows = df.iloc[0]['rows']
        if rows < min_rows:
            print(f"[ERROR] Not enough data in {table_name}. Found {rows}, need at least {min_rows}.")
            return False
        print(f"[OK] Verified training data: {rows} rows available in {table_name}.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to verify data: {e}")
        return False
    finally:
        conn.close()


def train_agent(env, model_path, total_timesteps=200_000, tensorboard_log=None):
    """
    Trains a PPO agent.

    Args:
        env: Gym-compatible environment.
        model_path (str): Path to save the trained model.
        total_timesteps (int): Number of training steps.
        tensorboard_log (str or None): Directory for TensorBoard logs.
    """
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=tensorboard_log)
    model.learn(total_timesteps=total_timesteps)
    model.save(model_path)
    print(f"[OK] Model saved to: {model_path}.zip")


if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('trading_ai_project/models', exist_ok=True)

    # Load configuration
    config_path = os.path.join('trading_ai_project', 'config.yaml')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Verify training data
    db_path = os.path.join('trading_ai_project', 'database', 'trading_data.db')
    if not verify_training_data(db_path):
        raise SystemExit("Training aborted: insufficient or missing data.")

    # Initialize environment
    env = DummyVecEnv([lambda: TradingEnv(config)])

    # Define paths
    model_path = os.path.join('trading_ai_project', 'models', 'ppo_trading_agent')
    tensorboard_log_dir = os.path.join('trading_ai_project', 'models', 'tensorboard')

    # Train the agent
    train_agent(env, model_path, total_timesteps=200_000, tensorboard_log=tensorboard_log_dir)

    print("[DONE] Training finished successfully.")
    print(f"TensorBoard logs: {tensorboard_log_dir}")
