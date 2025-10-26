import unittest
import yaml
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from trading_ai_project.env.gym_env import TradingEnv

class TestFeeSlippage(unittest.TestCase):

    def setUp(self):
        """Set up a test environment with a fixed configuration."""
        test_config = {
            'database': {
                'path': 'trading_ai_project/database/trading_data.db'
            },
            'gym_env': {
                'initial_balance': 10000,
                'lookback_window': 5, # Smaller window for faster test setup
                'fee_per_side': 0.01,  # 1% fee for easy calculation
                'slippage_factor': 0.02, # 2% slippage factor
                'max_drawdown': 0.5,
                'max_exposure': 0.9,
                'position_sizing': {
                    'method': 'fixed',
                    'fixed_size': 0.1 # 10% of balance
                }
            },
            'logging': {
                'level': 'DEBUG'
            }
        }
        self.env = TradingEnv(test_config)
        self.env.reset()
        # Manually set the current step and price for predictability
        self.env.current_step = 5
        self.env.df.loc[self.env.current_step, 'market_price'] = 100

    def test_buy_transaction_costs(self):
        """Test if fees and slippage are applied correctly on a buy order."""
        # Arrange
        initial_balance = self.env.balance
        current_price = self.env.df.loc[self.env.current_step, 'market_price']

        # Action: Buy
        shares_to_buy = self.env._calculate_position_size(current_price)
        slippage_amount = self.env.slippage_factor * (shares_to_buy ** 2)
        buy_price = current_price * (1 + slippage_amount)
        fee_amount = shares_to_buy * buy_price * self.env.fee
        expected_cost = (shares_to_buy * buy_price) + fee_amount

        # Act
        self.env.step(1) # Action 1 is Buy

        # Assert
        final_balance = self.env.balance
        actual_cost = initial_balance - final_balance

        self.assertAlmostEqual(actual_cost, expected_cost, places=5)
        self.assertEqual(self.env.shares_held, shares_to_buy)

    def test_sell_transaction_costs(self):
        """Test if fees and slippage are applied correctly on a sell order."""
        # Arrange
        # Give the environment some shares to sell
        self.env.shares_held = 10
        initial_balance = self.env.balance
        current_price = self.env.df.loc[self.env.current_step, 'market_price']

        # Action: Sell
        shares_to_sell = self.env._calculate_position_size(current_price)
        shares_to_sell = min(shares_to_sell, self.env.shares_held)

        slippage_amount = self.env.slippage_factor * (shares_to_sell ** 2)
        sell_price = current_price * (1 - slippage_amount)
        fee_amount = shares_to_sell * sell_price * self.env.fee
        expected_revenue = (shares_to_sell * sell_price) - fee_amount

        # Act
        self.env.step(2) # Action 2 is Sell

        # Assert
        final_balance = self.env.balance
        actual_revenue = final_balance - initial_balance

        self.assertAlmostEqual(actual_revenue, expected_revenue, places=5)
        self.assertAlmostEqual(self.env.shares_held, 10 - shares_to_sell, places=5)

if __name__ == '__main__':
    unittest.main()
