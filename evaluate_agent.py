import os
import numpy as np
import yaml
from stable_baselines3 import PPO
from trading_ai_project.env.gym_env import TradingEnv
import matplotlib.pyplot as plt

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

    plt.show()

if __name__ == '__main__':
    config_path = os.path.join('trading_ai_project', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    env = TradingEnv(config)

    model_path = "trading_ai_project/models/ppo_trading_agent.zip"
    model = PPO.load(model_path, env=env)

    rewards, net_worths = evaluate_agent(env, model)

    # The plot_results function will not work in this environment,
    # but we can at least check if the evaluation runs without errors.
    print("Evaluation finished.")
    print(f"Final net worth: {net_worths[-1]}")
