import pyodbc
import pandas as pd
from typing import List, Tuple, Optional, Dict, Any
import logging
from config.config_processor import ConfigProcessor

logger = logging.getLogger(__name__)


class DBConnector:
    def __init__(self, config: ConfigProcessor):
        self.config = config
        self.connection_string = self._build_connection_string()

    def _build_connection_string(self) -> str:
        db_config = self.config.get_database_config()
        return (
            f"DRIVER={{{db_config['driver']}}};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']};"
            f"Trusted_Connection={db_config['trusted_connection']};"
            f"Encrypt={db_config['encrypt']};"
        )

    def get_connection(self):
        """Get a new database connection"""
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except pyodbc.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def execute_query(self, query: str, params: Tuple = None) -> Optional[pd.DataFrame]:
        """Execute a query and return results as DataFrame if applicable"""
        conn = self.get_connection()
        try:
            if query.strip().upper().startswith('SELECT'):
                # Use pyodbc cursor directly to avoid pandas warning
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Get column names
                columns = [column[0] for column in cursor.description] if cursor.description else []

                # Fetch all data
                data = cursor.fetchall()

                # Convert to DataFrame
                if columns and data:
                    df = pd.DataFrame.from_records(data, columns=columns)
                else:
                    df = pd.DataFrame()

                return df
            else:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return None
        except Exception as e:
            conn.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            conn.close()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        query = """
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ?
        """
        try:
            result = self.execute_query(query, (table_name,))
            return result.iloc[0, 0] > 0
        except:
            return False

    def create_table_from_schema(self, table_name: str, schema: Dict[str, str]):
        """Create a table based on the provided schema"""
        columns = []
        for col_name, col_type in schema.items():
            columns.append(f"[{col_name}] {col_type}")

        create_table_sql = f"CREATE TABLE [{table_name}] (\n    " + ",\n    ".join(columns) + "\n)"

        self.execute_query(create_table_sql)
        logger.info(f"Created table: {table_name}")