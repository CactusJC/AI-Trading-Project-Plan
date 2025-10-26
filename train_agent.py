import os
import yaml
from stable_baselines3 import PPO
from trading_ai_project.env.gym_env import TradingEnv

def train_agent(env, model_path, total_timesteps=20000):
    """
    Trains the PPO agent.
    """
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=total_timesteps)
    model.save(model_path)

if __name__ == '__main__':
    # Load configuration
    config_path = os.path.join('trading_ai_project', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Instantiate the environment with the configuration
    env = TradingEnv(config)

    model_path = "trading_ai_project/models/ppo_trading_agent"
    train_agent(env, model_path)

    print(f"Training finished. Model saved to {model_path}.zip")