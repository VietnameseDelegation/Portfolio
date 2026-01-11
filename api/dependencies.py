from config.config_processor import ConfigProcessor
from database.db_connector import DBConnector

def get_db_connector():
    # Assuming config.ini is in the root directory relative to where the app runs
    # If main.py sets cwd correctly, this works.
    config = ConfigProcessor('config.ini')
    return DBConnector(config)
