import os
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from trading_ai_project.env.gym_env import TradingEnv

def evaluate_agent(env, model):
    """
    Evaluates the trained agent.
    """
    obs, info = env.reset()
    done = False
    rewards = []
    net_worths = []

    while not done:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        rewards.append(reward)
        net_worths.append(env.net_worth)

    return rewards, net_worths

def plot_results(rewards, net_worths):
    """
    Plots the results of the evaluation.
    """
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 2, 1)
    plt.plot(rewards)
    plt.title('Rewards')

    plt.subplot(1, 2, 2)
    plt.plot(net_worths)
    plt.title('Net Worth')

    # Save the plot to a file
    plt.savefig('trading_ai_project/performance.png')
    print("Performance plot saved to trading_ai_project/performance.png")

if __name__ == '__main__':
    db_path = os.path.join('trading_ai_project', 'database', 'trading_data.db')
    env = TradingEnv(db_path)

    model_path = "trading_ai_project/models/ppo_trading_agent.zip"
    model = PPO.load(model_path, env=env)

    rewards, net_worths = evaluate_agent(env, model)

    plot_results(rewards, net_worths)
