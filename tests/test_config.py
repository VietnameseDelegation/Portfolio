import unittest
from unittest.mock import MagicMock, patch
from config.config_processor import ConfigProcessor
from common.exceptions import ConfigurationError

class TestConfigProcessor(unittest.TestCase):

    @patch('config.config_processor.configparser.ConfigParser')
    @patch('config.config_processor.Path.mkdir')
    def test_init_valid_config(self, mock_mkdir, mock_config_parser):
        # Mock successful read and validation
        mock_instance = mock_config_parser.return_value
        
        def getitem_side_effect(key):
            if key == 'DATABASE':
                return {
                    'server': 'localhost',
                    'database': 'testdb',
                    'driver': 'SQL Server',
                    'username': 'user', 
                    'password': 'password',
                    'trusted_connection': 'yes',
                    'encrypt': 'no'
                }
            elif key == 'IMPORT':
                 return {
                    'input_folder': 'input',
                    'processed_folder': 'input/processed',
                    'rejects_folder': 'rejects',
                    'scan_rows': '100',
                    'batch_size': '1000',
                    'varchar_length': '255',
                    'fast_executemany': 'true'
                 }
            elif key == 'EXPORT':
                 return {'export_folder': 'export'}
            raise KeyError(key)

        mock_instance.__getitem__.side_effect = getitem_side_effect
        # Mock contains check
        mock_instance.__contains__.side_effect = lambda x: x in ['DATABASE', 'IMPORT', 'EXPORT']
        
        # Should not raise
        config = ConfigProcessor()
        self.assertIsNotNone(config)

    @patch('config.config_processor.configparser.ConfigParser')
    def test_init_missing_critical_section(self, mock_config_parser):
        mock_instance = mock_config_parser.return_value
        # Mock missing DATABASE section
        mock_instance.__getitem__.side_effect = KeyError('DATABASE')
        
        with self.assertRaises(ConfigurationError):
            ConfigProcessor()

    @patch('config.config_processor.configparser.ConfigParser')
    def test_init_missing_required_field(self, mock_config_parser):
        mock_instance = mock_config_parser.return_value
        # Mock DATABASE section but missing 'server'
        mock_instance.__getitem__.return_value = {
            'server': '', # Empty server
            'database': 'testdb',
            'driver': 'SQL Server'
        }
        
        with self.assertRaises(ConfigurationError) as cm:
            ConfigProcessor()
        self.assertIn("Missing required database configuration: server", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
