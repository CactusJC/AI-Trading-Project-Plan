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

    # Match buy/sell trades using FIFO
    open_positions = [] # List of {'price': float, 'shares': float, 'fee': float}
    completed_trades = [] # List of {'profit': float, 'buy_price': float, 'sell_price': float, 'shares': float}

    for trade in trade_history:
        if trade['action'] == 'buy':
            # Add new position to queue
            # Fee per share for this batch
            fee_per_share = trade['fee'] / trade['shares'] if trade['shares'] > 0 else 0
            open_positions.append({
                'price': trade['price'],
                'shares': trade['shares'],
                'fee_per_share': fee_per_share
            })

        elif trade['action'] == 'sell':
            shares_to_sell = trade['shares']
            sell_fee_per_share = trade['fee'] / trade['shares'] if trade['shares'] > 0 else 0

            while shares_to_sell > 0 and open_positions:
                buy_pos = open_positions[0] # FIFO: take from oldest

                matched_shares = min(shares_to_sell, buy_pos['shares'])

                # Calculate profit for this matched portion
                # Revenue - Cost - BuyFee - SellFee
                revenue = matched_shares * trade['price']
                cost = matched_shares * buy_pos['price']
                buy_fee = matched_shares * buy_pos['fee_per_share']
                sell_fee = matched_shares * sell_fee_per_share

                profit = revenue - cost - buy_fee - sell_fee
                completed_trades.append(profit)

                # Update remaining shares
                shares_to_sell -= matched_shares
                buy_pos['shares'] -= matched_shares

                if buy_pos['shares'] < 1e-9: # Effectively zero
                    open_positions.pop(0)

    total_round_trips = len(completed_trades)
    winning_trades = sum(1 for p in completed_trades if p > 0)
    win_rate = winning_trades / total_round_trips if total_round_trips > 0 else 0

    print("\n--- Performance Metrics ---")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Total Round-Trip Trades (FIFO matched): {total_round_trips}")
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
