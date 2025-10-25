import time
import os
import json
from trading_ai_project.api.lnmarkets_client import get_lnmarkets_client
from stable_baselines3 import PPO
from trading_ai_project.env.gym_env import TradingEnv
import numpy as np
import talib

def get_live_market_data(client):
    """
    Fetches live OHLC data from LN Markets.
    """
    ohlc = client.get_ohlc('BTCUSD', '1m', 1)
    if ohlc and len(ohlc) > 0:
        latest_candle = ohlc[0]
        return {
            'market_price': latest_candle['c'],
            'high': latest_candle['h'],
            'low': latest_candle['l'],
            'open': latest_candle['o'],
            'volume': latest_candle['v']
        }
    return None

def run_live_trading(client, model, env):
    """
    Runs the live trading simulation.
    """
    print("Starting live trading simulation...")
    while True:
        # Fetch live market data
        market_data = get_live_market_data(client)

        if market_data:
            # Update the environment with the latest market data
            # This is a simplified approach; a real implementation would
            # require updating the environment's internal state more carefully.
            env.df.loc[len(env.df)] = [
                time.time(), market_data['market_price'], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ]
            env._add_technical_indicators()

            # Get the latest observation
            obs = env._next_observation()

            # Get the agent's action
            action, _states = model.predict(obs, deterministic=True)

            # Execute the action (in a real scenario, you would place orders here)
            if action == 1:
                print("Action: Buy")
                # client.new_position(...)
            elif action == 2:
                print("Action: Sell")
                # client.close_position(...)
            else:
                print("Action: Hold")

        # Wait for the next candle
        time.sleep(60)

if __name__ == '__main__':
    client = get_lnmarkets_client()

    db_path = os.path.join('trading_ai_project', 'database', 'trading_data.db')
    env = TradingEnv(db_path)

    model_path = "trading_ai_project/models/ppo_trading_agent.zip"
    model = PPO.load(model_path, env=env)

    # Note: Running this script will start an infinite loop.
    # I will not run this script as part of the automated process,
    # but the code is here for the user to run.
    # run_live_trading(client, model, env)
    print("Live trading script created. To run, uncomment the last line.")
