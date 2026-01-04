from typing import List, Dict, Any, Optional
from datetime import datetime
from database.db_connector import DBConnector
from models.user import UserDTO
from models.product import ProductDTO
from models.order import OrderDTO
from dao.user_dao import UserDAO
from dao.order_dao import OrderDAO
from dao.order_item_dao import OrderItemDAO

class OrderService:
    def __init__(self, connector: DBConnector):
        self.connector = connector
        self.user_dao = UserDAO(connector)
        self.order_dao = OrderDAO(connector)
        self.item_dao = OrderItemDAO(connector)

    def create_order_process(self, user: UserDTO, status: str, items: List[ProductDTO], quantities: List[int]) -> int:
        if len(items) != len(quantities):
            raise ValueError("Items and quantities must have the same length")

        # 1. Handle User
        existing_user = self.user_dao.get_by_email(user.email)
        if existing_user:
            user_id = existing_user.id
        else:
            user_id = self.user_dao.create(user)

        # 2. Create Order
        new_order = OrderDTO(
            id=0, # Placeholder
            user_id=user_id,
            order_date=datetime.now(),
            status=status,
            paid=False
        )
        order_id = self.order_dao.create(new_order)

        # 3. Create Items
        for item, qty in zip(items, quantities):
            self.item_dao.create(item, order_id, qty)
            
        return order_id

    def get_order_details(self, order_id: int) -> Optional[Dict[str, Any]]:
        # 1. Get Order
        order = self.order_dao.get_by_id(order_id)
        if not order:
            return None
            
        # 2. Get User
        user = self.user_dao.get_by_id(order.user_id)
        
        # 3. Get Items
        items = self.item_dao.get_by_order_id(order_id)
        
        return {
            "order_id": order.id,
            "order_date": order.order_date,
            "status": order.status,
            "paid": order.paid,
            "user": {
                "id": user.id if user else None,
                "name": user.name if user else "Unknown",
                "email": user.email if user else "Unknown"
            },
            "items": items
        }

    def delete_order_process(self, order_id: int):
        # 1. Delete Items
        self.item_dao.delete_by_order_id(order_id)
        
        # 2. Delete Order
        self.order_dao.delete(order_id)
