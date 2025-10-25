from trading_ai_project.env.gym_env import TradingEnv
import matplotlib.pyplot as plt
import numpy as np

def run_backtest(env, episodes=1):
    """
    Runs a simple backtest with random actions.
    """
    rewards = []
    net_worths = []

    for _ in range(episodes):
        obs, info = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()  # Take a random action
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            rewards.append(reward)
            net_worths.append(env.net_worth)

    return rewards, net_worths

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

if __name__ == '__main__':
    env = TradingEnv('trading_ai_project/database/trading_data.db')
    rewards, net_worths = run_backtest(env, episodes=1)
    # The plot_results function will not work in this environment,
    # but we can at least check if the backtest runs without errors.
    print("Backtest finished.")
    print(f"Final net worth: {net_worths[-1]}")
