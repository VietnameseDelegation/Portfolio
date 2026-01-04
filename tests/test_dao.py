import unittest
from unittest.mock import MagicMock
import pandas as pd
from dao.product_dao import ProductDAO
from dao.order_item_dao import OrderItemDAO
from models.product import ProductDTO
from models.order_item import OrderItemDTO

class TestDAOs(unittest.TestCase):
    def setUp(self):
        self.mock_connector = MagicMock()

    def test_product_dao_get_by_id(self):
        # Setup mock return
        self.mock_connector.execute_query.return_value = pd.DataFrame([{
            'id': 1, 'name': 'Test Product', 'price': 10.0, 'category_id': 1, 'active': True
        }])
        
        dao = ProductDAO(self.mock_connector)
        product = dao.get_by_id(1)
        
        self.assertIsNotNone(product)
        self.assertIsInstance(product, ProductDTO)
        self.assertEqual(product.name, 'Test Product')

    def test_product_dao_get_by_id_none(self):
        self.mock_connector.execute_query.return_value = pd.DataFrame() # Empty
        
        dao = ProductDAO(self.mock_connector)
        product = dao.get_by_id(999)
        
        self.assertIsNone(product)

    def test_order_item_dao_get_by_order_id(self):
        self.mock_connector.execute_query.return_value = pd.DataFrame([{
            'order_id': 100, 'product_id': 1, 'quantity': 2, 'price_at_order': 10.0
        }])
        
        dao = OrderItemDAO(self.mock_connector)
        items = dao.get_by_order_id(100)
        
        self.assertEqual(len(items), 1)
        self.assertIsInstance(items[0], OrderItemDTO)
        self.assertEqual(items[0].quantity, 2)

if __name__ == '__main__':
    unittest.main()
