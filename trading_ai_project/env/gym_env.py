import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import sqlite3
import talib

class TradingEnv(gym.Env):
    """Custom Environment for Bitcoin Trading"""
    metadata = {'render.modes': ['human']}

    def __init__(self, db_filepath, initial_balance=10000, lookback_window=20, fee=0.00015, slippage_factor=0.0001, max_drawdown=0.2):
        super(TradingEnv, self).__init__()

        # Load data and calculate indicators
        conn = sqlite3.connect(db_filepath)
        self.df = pd.read_sql_query("SELECT * FROM btc_daily_data", conn)
        conn.close()
        self.df = self.df.sort_values('timestamp').reset_index(drop=True)
        self._add_technical_indicators()

        self.initial_balance = initial_balance
        self.lookback_window = lookback_window
        self.current_step = self.lookback_window
        self.fee = fee
        self.slippage_factor = slippage_factor
        self.max_drawdown = max_drawdown
        self.peak_net_worth = initial_balance

        # Define action space: 0: Hold, 1: Buy, 2: Sell
        self.action_space = spaces.Discrete(3)

        # Define observation space
        # Columns: market_price, balance, shares_held, RSI, MACD, UpperBB, MiddleBB, LowerBB
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32
        )

        self.reset()

    def _add_technical_indicators(self):
        self.df['RSI'] = talib.RSI(self.df['market_price'])
        macd, macdsignal, macdhist = talib.MACD(self.df['market_price'])
        self.df['MACD'] = macd
        upper, middle, lower = talib.BBANDS(self.df['market_price'])
        self.df['UpperBB'], self.df['MiddleBB'], self.df['LowerBB'] = upper, middle, lower
        self.df.dropna(inplace=True)
        self.df = self.df.reset_index(drop=True)


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.prev_net_worth = self.initial_balance
        self.peak_net_worth = self.initial_balance
        self.current_step = self.lookback_window

        obs = self._next_observation()
        info = {}
        return obs, info

    def _next_observation(self):
        obs = np.array([
            self.df.loc[self.current_step, 'market_price'],
            self.balance,
            self.shares_held,
            self.df.loc[self.current_step, 'RSI'],
            self.df.loc[self.current_step, 'MACD'],
            self.df.loc[self.current_step, 'UpperBB'],
            self.df.loc[self.current_step, 'MiddleBB'],
            self.df.loc[self.current_step, 'LowerBB']
        ])
        return obs

    def step(self, action):
        # Execute one time step within the environment
        self._take_action(action)

        self.current_step += 1
        self.peak_net_worth = max(self.peak_net_worth, self.net_worth)

        # Check if we're at the end of the dataset
        if self.current_step >= len(self.df) - 1:
            terminated = True
        else:
            terminated = False

        truncated = False

        reward = self.net_worth - self.prev_net_worth
        self.prev_net_worth = self.net_worth

        drawdown = (self.peak_net_worth - self.net_worth) / self.peak_net_worth
        if drawdown > self.max_drawdown:
            reward -= 100  # Penalty for exceeding max drawdown

        obs = self._next_observation()
        info = {}

        return obs, reward, terminated, truncated, info

    def _take_action(self, action):
        current_price = self.df.loc[self.current_step, 'market_price']

        if action == 1:  # Buy
            shares_to_buy = (self.balance * 0.1) / current_price if current_price > 0 else 0
            slippage = self.slippage_factor * (shares_to_buy ** 2)
            buy_price = current_price * (1 + slippage)
            cost = shares_to_buy * buy_price * (1 + self.fee)
            if self.balance > cost:
                self.shares_held += shares_to_buy
                self.balance -= cost

        elif action == 2:  # Sell
            shares_to_sell = self.shares_held * 0.1
            slippage = self.slippage_factor * (shares_to_sell ** 2)
            sell_price = current_price * (1 - slippage)
            if self.shares_held > shares_to_sell:
                revenue = shares_to_sell * sell_price * (1 - self.fee)
                self.shares_held -= shares_to_sell
                self.balance += revenue

        self.net_worth = self.balance + self.shares_held * current_price

    def render(self, mode='human', close=False):
        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance}')
        print(f'Shares held: {self.shares_held}')
        print(f'Net Worth: {self.net_worth}')
