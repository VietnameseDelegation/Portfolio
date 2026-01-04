import pyodbc
import pandas as pd
from typing import Tuple, Optional, Dict
import logging
from config.config_processor import ConfigProcessor as ConfigProcessor
from common.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class DBConnector:
    def __init__(self, config: ConfigProcessor):
        self.config = config
        self.connection_string = self._build_connection_string()

    def _build_connection_string(self) -> str:
        try:
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
        except Exception as e:
            raise DatabaseError(f"Failed to build connection string: {e}")

    def get_connection(self):
        """Get a new database connection"""
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except pyodbc.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise DatabaseError(f"Could not connect to database: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to database: {e}")
            raise DatabaseError(f"Unexpected connection error: {e}")

    def execute_query(self, query: str, params: Tuple = None) -> Optional[pd.DataFrame]:
        """Execute a query and return results as DataFrame if applicable"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Iterate to find the first result set that has data
            while True:
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    data = cursor.fetchall()
                    conn.commit()
                    if columns and data:
                        return pd.DataFrame.from_records(data, columns=columns)
                    else:
                        return pd.DataFrame(columns=columns)
                
                if not cursor.nextset():
                    break
            
            conn.commit()
            return None
        except pyodbc.Error as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            logger.error(f"Query execution failed: {e}")
            raise DatabaseError(f"Error executing query: {e}")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            logger.error(f"Unexpected error during query execution: {e}")
            raise DatabaseError(f"Unexpected query error: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

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
        except DatabaseError:
            return False
        except Exception:
            return False

    def create_table_from_schema(self, table_name: str, schema: Dict[str, str]):
        """Create a table based on the provided schema"""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"[{col_name}] {col_type}")

            create_table_sql = f"CREATE TABLE [{table_name}] (\n    " + ",\n    ".join(columns) + "\n)"

            self.execute_query(create_table_sql)
            logger.info(f"Created table: {table_name}")
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            raise DatabaseError(f"Failed to create table {table_name}: {e}")
