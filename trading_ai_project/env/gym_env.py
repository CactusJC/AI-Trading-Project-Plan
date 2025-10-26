import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import sqlite3
import talib
import yaml
import logging

class TradingEnv(gym.Env):
    """Custom Environment for Bitcoin Trading"""
    metadata = {'render.modes': ['human']}

    def __init__(self, config):
        super(TradingEnv, self).__init__()

        # Configure logging
        log_level = config['logging'].get('level', 'INFO').upper()
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)

        # Load data and calculate indicators
        db_filepath = config['database']['path']
        conn = sqlite3.connect(db_filepath)
        self.df = pd.read_sql_query("SELECT * FROM btc_daily_data", conn)
        conn.close()
        self.df = self.df.sort_values('timestamp').reset_index(drop=True)
        self._add_technical_indicators()

        self.initial_balance = config['gym_env']['initial_balance']
        self.lookback_window = config['gym_env']['lookback_window']
        self.fee = config['gym_env']['fee_per_side']
        self.slippage_factor = config['gym_env']['slippage_factor']
        self.max_drawdown = config['gym_env']['max_drawdown']
        self.position_sizing_config = config['gym_env']['position_sizing']
        self.max_exposure = config['gym_env'].get('max_exposure', 0.5) # Max exposure as a fraction of net worth


        self.current_step = self.lookback_window
        self.peak_net_worth = self.initial_balance

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
        self.trade_history = []

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

    def _calculate_position_size(self, current_price):
        method = self.position_sizing_config.get('method', 'fixed')

        if method == 'volatility_scaled':
            volatility_window = self.position_sizing_config.get('volatility_window', 20)
            risk_factor = self.position_sizing_config.get('risk_factor', 0.05)

            start_index = max(0, self.current_step - volatility_window)
            historical_prices = self.df.loc[start_index:self.current_step, 'market_price']
            volatility = historical_prices.std()

            if volatility > 0:
                return (self.net_worth * risk_factor) / volatility
            else:
                return 0 # Avoid division by zero
        else: # Default to 'fixed'
            fixed_size = self.position_sizing_config.get('fixed_size', 0.1)
            return self.balance * fixed_size / current_price

    def _take_action(self, action):
        current_price = self.df.loc[self.current_step, 'market_price']

        if action == 1:  # Buy
            shares_to_buy = self._calculate_position_size(current_price)
            current_exposure = (self.shares_held * current_price) / self.net_worth

            if current_exposure + (shares_to_buy * current_price / self.net_worth) > self.max_exposure:
                shares_to_buy = 0

            slippage = self.slippage_factor * (shares_to_buy ** 2)
            buy_price = current_price * (1 + slippage)

            transaction_value = shares_to_buy * buy_price
            fee_amount = transaction_value * self.fee
            cost = transaction_value + fee_amount

            if self.balance > cost and shares_to_buy > 0:
                self.shares_held += shares_to_buy
                self.balance -= cost
                trade_info = {
                    'step': self.current_step,
                    'action': 'buy',
                    'price': buy_price,
                    'shares': shares_to_buy,
                    'fee': fee_amount,
                    'slippage': slippage
                }
                self.trade_history.append(trade_info)
                self.logger.debug(f"Executed Buy: {trade_info}")

        elif action == 2:  # Sell
            shares_to_sell = self.shares_held # Simple strategy: sell all held shares

            slippage = self.slippage_factor * (shares_to_sell ** 2)
            sell_price = current_price * (1 - slippage)

            if shares_to_sell > 0:
                transaction_value = shares_to_sell * sell_price
                fee_amount = transaction_value * self.fee
                revenue = transaction_value - fee_amount
                self.shares_held -= shares_to_sell
                self.balance += revenue
                trade_info = {
                    'step': self.current_step,
                    'action': 'sell',
                    'price': sell_price,
                    'shares': shares_to_sell,
                    'fee': fee_amount,
                    'slippage': slippage
                }
                self.trade_history.append(trade_info)
                self.logger.debug(f"Executed Sell: {trade_info}")

        self.net_worth = self.balance + self.shares_held * current_price

    def render(self, mode='human', close=False):
        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance}')
        print(f'Shares held: {self.shares_held}')
        print(f'Net Worth: {self.net_worth}')
