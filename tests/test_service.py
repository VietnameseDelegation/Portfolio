import unittest
from unittest.mock import MagicMock, patch
from service.order_service import OrderService
from models.user import UserDTO
from models.product import ProductDTO
from common.exceptions import ValidationError

class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.mock_connector = MagicMock()
        self.service = OrderService(self.mock_connector)
        # Mock internal DAOs since they are created in __init__
        self.service.user_dao = MagicMock()
        self.service.order_dao = MagicMock()
        self.service.item_dao = MagicMock()
        self.service.product_dao = MagicMock()

    def test_create_order_valid(self):
        user = UserDTO(0, "Test", "test@example.com", None)
        products = [ProductDTO(1, "Prod", 10.0, 1, True)]
        quantities = [2]
        
        # Mocks
        self.service.user_dao.get_by_email.return_value = None
        self.service.user_dao.create.return_value = 101 # new user id
        self.service.order_dao.create.return_value = 500 # new order id
        
        order_id = self.service.create_order_process(user, "PENDING", products, quantities)
        
        self.assertEqual(order_id, 500)
        self.service.user_dao.create.assert_called_once()
        self.service.item_dao.create.assert_called_once()

    def test_create_order_invalid_email(self):
        user = UserDTO(0, "Test", "invalid", None)
        with self.assertRaises(ValidationError) as cm:
            self.service.create_order_process(user, "PENDING", [], [])
        self.assertIn("Invalid email", str(cm.exception))

    def test_create_order_empty_items(self):
        user = UserDTO(0, "Test", "test@example.com", None)
        with self.assertRaises(ValidationError) as cm:
             self.service.create_order_process(user, "PENDING", [], [])
        self.assertIn("at least one item", str(cm.exception))

    def test_create_order_negative_quantity(self):
        user = UserDTO(0, "Test", "test@example.com", None)
        products = [ProductDTO(1, "Prod", 10.0, 1, True)]
        quantities = [-1]
        
        with self.assertRaises(ValidationError) as cm:
            self.service.create_order_process(user, "PENDING", products, quantities)
        self.assertIn("greater than zero", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
