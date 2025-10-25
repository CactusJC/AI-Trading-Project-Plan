import os
from stable_baselines3 import PPO
from trading_ai_project.env.gym_env import TradingEnv

def train_agent(env, total_timesteps=20000):
    """
    Trains a PPO agent on the custom trading environment.
    """
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=total_timesteps)
    return model

def save_model(model, save_path):
    """
    Saves the trained model to a file.
    """
    model.save(save_path)

if __name__ == '__main__':
    db_path = os.path.join('trading_ai_project', 'database', 'trading_data.db')
    env = TradingEnv(db_path)

    model = train_agent(env)

    models_dir = "trading_ai_project/models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    save_model(model, f"{models_dir}/ppo_trading_agent")

    print("Training finished and model saved.")
