from typing import List
from database.db_connector import DBConnector
from models.product import ProductDTO
from models.order_item import OrderItemDTO

class OrderItemDAO:
    def __init__(self, connector: DBConnector):
        self.connector = connector

    def create(self, item: ProductDTO, order_id: int, quantity: int):
        query = "INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES (?, ?, ?, ?)"
        self.connector.execute_query(query, (order_id, item.id, quantity, item.price))

    def get_by_order_id(self, order_id: int) -> List[OrderItemDTO]:
        query = "SELECT order_id, product_id, quantity, price_at_order FROM order_items WHERE order_id = ?"
        result = self.connector.execute_query(query, (order_id,))
        
        items = []
        if not result.empty:
            for _, row in result.iterrows():
                items.append(OrderItemDTO(
                    order_id=int(row['order_id']),
                    product_id=int(row['product_id']),
                    quantity=int(row['quantity']),
                    price_at_order=float(row['price_at_order'])
                ))
        return items

    def delete_by_order_id(self, order_id: int):
        self.connector.execute_query("DELETE FROM order_items WHERE order_id = ?", (order_id,))
