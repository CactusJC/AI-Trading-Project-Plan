import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading_ai_project.env.gym_env import TradingEnv
import matplotlib.pyplot as plt
import numpy as np

def run_backtest(env, episodes=1):
    """
    Runs a simple backtest with random actions.
    """
    rewards = []
    net_worths = []
    trade_history = []

    for _ in range(episodes):
        obs, info = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()  # Take a random action
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            rewards.append(reward)
            net_worths.append(env.net_worth)
        trade_history.extend(env.trade_history)

    return rewards, net_worths, trade_history


def calculate_and_print_kpis(net_worths, trade_history):
    """
    Calculates and prints key performance indicators by analyzing round-trip trades.
    """
    if not trade_history:
        print("No trades were made.")
        return

    returns = np.diff(net_worths) / net_worths[:-1]
    sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0

    buy_trades = [t for t in trade_history if t['action'] == 'buy']
    sell_trades = [t for t in trade_history if t['action'] == 'sell']

    # Simple pairing of buy and sell trades for win rate calculation
    # This assumes a LIFO (last-in, first-out) trading strategy for simplicity
    round_trips = []
    while buy_trades and sell_trades:
        buy = buy_trades.pop(0)

        # Find the corresponding sell trade (can be more complex in real scenarios)
        corresponding_sell = None
        for sell in sell_trades:
            if sell['step'] > buy['step']:
                corresponding_sell = sell
                break

        if corresponding_sell:
            profit = (corresponding_sell['price'] * corresponding_sell['shares']) - \
                     (buy['price'] * buy['shares']) - \
                     (buy['fee'] + corresponding_sell['fee'])
            round_trips.append(profit)
            sell_trades.remove(corresponding_sell)

    total_round_trips = len(round_trips)
    winning_trades = sum(1 for p in round_trips if p > 0)
    win_rate = winning_trades / total_round_trips if total_round_trips > 0 else 0

    print("\n--- Performance Metrics ---")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Total Round-Trip Trades: {total_round_trips}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Final Net Worth: {net_worths[-1]:.2f}")
    print("-------------------------\n")

def plot_results(rewards, net_worths):
    """
    Plots the results of the backtest.
    """
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 2, 1)
    plt.plot(rewards)
    plt.title('Rewards')

    plt.subplot(1, 2, 2)
    plt.plot(net_worths)
    plt.title('Net Worth')

    plt.show()

import yaml

if __name__ == '__main__':
    # Load configuration
    config_path = os.path.join('trading_ai_project', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Instantiate the environment with the configuration
    env = TradingEnv(config)

    rewards, net_worths, trade_history = run_backtest(env, episodes=1)

    print("Backtest finished.")
    calculate_and_print_kpis(net_worths, trade_history)
