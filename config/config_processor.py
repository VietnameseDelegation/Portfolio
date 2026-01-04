import configparser
import os
from pathlib import Path
from typing import Dict, Any
from common.exceptions import ConfigurationError


class ConfigProcessor:
    def __init__(self, config_path: str = "config.ini"):
        self.config = configparser.ConfigParser()
        self.config_path = config_path
        self.load_config()
        self.validate_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            self.create_default_config()
        self.config.read(self.config_path)

    def validate_config(self):
        """Validates that critical configuration is present"""
        try:
            db_config = self.config['DATABASE']
            required_fields = ['server', 'database', 'driver']
            
            for field in required_fields:
                if not db_config.get(field):
                    raise ConfigurationError(f"Missing required database configuration: {field}")
                    
        except KeyError as e:
            raise ConfigurationError(f"Missing configuration section: {e}")

    def create_default_config(self):
        """Create default configuration file if it doesn't exist"""
        self.config['DATABASE'] = {
            'server': '',
            'database': 'OrderSystem',
            'username': '',
            'password': '',
            'driver': 'ODBC Driver 17 for SQL Server',
            'trusted_connection': 'no',
            'encrypt':'no'
        }

        self.config['IMPORT'] = {
            'input_folder': 'input',
            'processed_folder': 'input/processed',
            'rejects_folder': 'rejects',
            'scan_rows': '100',
            'batch_size': '1000',
            'varchar_length': '255',
            'fast_executemany': 'true'
        }

        self.config['EXPORT'] = {
            'export_folder': 'export'
        }

        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

        # Create necessary directories
        self.mkdir_input_output_folder()



    def mkdir_input_output_folder(self):
        """Create input and output folder if it doesn't exist"""
        try:
            import_config = self.get_import_config()
            Path(import_config['input_folder']).mkdir(exist_ok=True)
            Path(import_config['processed_folder']).mkdir(parents=True, exist_ok=True)
            Path(import_config['rejects_folder']).mkdir(parents=True, exist_ok=True)
            Path(self.get_export_config()['export_folder']).mkdir(exist_ok=True)
        except Exception as e:
            raise ConfigurationError(f"Failed to create directories: {e}")

    def get_database_config(self) -> Dict[str, Any]:
        return dict(self.config['DATABASE'])

    def get_import_config(self) -> Dict[str, Any]:
        config_dict = dict(self.config['IMPORT'])
        # Convert numeric values
        try:
            config_dict['scan_rows'] = int(config_dict['scan_rows'])
            config_dict['batch_size'] = int(config_dict['batch_size'])
            config_dict['varchar_length'] = int(config_dict['varchar_length'])
            config_dict['fast_executemany'] = config_dict['fast_executemany'].lower() == 'true'
            return config_dict
        except ValueError as e:
             raise ConfigurationError(f"Invalid numeric value in IMPORT config: {e}")

    def get_export_config(self) -> Dict[str, str]:
        return dict(self.config['EXPORT'])
