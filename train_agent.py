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

import argparse
import os
import sqlite3

import pandas as pd
import yaml
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
    parser = argparse.ArgumentParser(description="Train the PPO trading agent.")
    parser.add_argument('--config', default=os.path.join('trading_ai_project', 'config.yaml'),
                        help='Path to YAML config file')
    parser.add_argument('--db-path', default=os.path.join('trading_ai_project', 'database', 'trading_data.db'),
                        help='SQLite database with price history')
    parser.add_argument('--table', default='btc_daily_data',
                        help='Table name inside the SQLite database')
    parser.add_argument('--timesteps', type=int, default=200_000,
                        help='Number of PPO training steps')
    parser.add_argument('--model-path', default=os.path.join('trading_ai_project', 'models', 'ppo_trading_agent'),
                        help='Output path (without .zip) for the trained model')
    parser.add_argument('--tensorboard-log', default=os.path.join('trading_ai_project', 'models', 'tensorboard'),
                        help='Directory to store TensorBoard logs')

    args = parser.parse_args()

    # Ensure directories exist
    os.makedirs(os.path.dirname(args.model_path), exist_ok=True)

    # Load configuration
    if not os.path.exists(args.config):
        raise FileNotFoundError(f"Configuration file not found: {args.config}")

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    # Override data source from CLI to keep environment data aligned
    config.setdefault('database', {})
    config['database']['path'] = args.db_path
    config['database']['table'] = args.table

    # Verify training data
    if not verify_training_data(args.db_path, table_name=args.table):
        raise SystemExit("Training aborted: insufficient or missing data.")

    # Initialize environment
    env = DummyVecEnv([lambda: TradingEnv(config)])

    # Train the agent
    train_agent(env, args.model_path, total_timesteps=args.timesteps, tensorboard_log=args.tensorboard_log)

    print("[DONE] Training finished successfully.")
    print(f"TensorBoard logs: {args.tensorboard_log}")
