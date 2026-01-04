import unittest
from unittest.mock import MagicMock, patch
import pyodbc
from database.db_connector import DBConnector
from common.exceptions import DatabaseError

class TestDBConnector(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.get_database_config.return_value = {
            'driver': 'SQL Driver',
            'server': 'localhost',
            'database': 'test_db',
            'username': 'user',
            'password': 'password',
            'trusted_connection': 'yes',
            'encrypt': 'no'
        }

    @patch('database.db_connector.pyodbc.connect')
    def test_get_connection_success(self, mock_connect):
        connector = DBConnector(self.mock_config)
        conn = connector.get_connection()
        self.assertTrue(mock_connect.called)
        self.assertIsNotNone(conn)

    @patch('database.db_connector.pyodbc.connect')
    def test_get_connection_failure(self, mock_connect):
        mock_connect.side_effect = pyodbc.Error('Connection failed')
        connector = DBConnector(self.mock_config)
        
        with self.assertRaises(DatabaseError) as cm:
            connector.get_connection()
        self.assertIn("Could not connect to database", str(cm.exception))

    @patch('database.db_connector.pyodbc.connect')
    def test_execute_query_success(self, mock_connect):
        connector = DBConnector(self.mock_config)
        
        # Mock cursor and data
        mock_cursor = MagicMock()
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [(1, 'test')]
        mock_cursor.nextset.return_value = False
        
        mock_conn = mock_connect.return_value
        mock_conn.cursor.return_value = mock_cursor
        
        df = connector.execute_query("SELECT * FROM table")
        
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], 'test')

    @patch('database.db_connector.pyodbc.connect')
    def test_execute_query_failure(self, mock_connect):
        connector = DBConnector(self.mock_config)
        mock_conn = mock_connect.return_value
        mock_conn.cursor.side_effect = pyodbc.Error("Query failed")
        
        with self.assertRaises(DatabaseError):
            connector.execute_query("SELECT * FROM table")

if __name__ == '__main__':
    unittest.main()
