import unittest

from trading_ai_project.main import load_config


class TestMainConfig(unittest.TestCase):
    def test_load_config_reads_project_defaults(self):
        config = load_config()

        self.assertIn('database', config)
        self.assertEqual(
            config['database']['path'],
            'trading_ai_project/database/trading_data.db'
        )
        self.assertEqual(
            config['database']['table'],
            'btc_daily_data'
        )


if __name__ == '__main__':
    unittest.main()
