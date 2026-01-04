from typing import List, Dict
from database.db_connector import DBConnector
from models.product import ProductDTO

class OrderItemDAO:
    def __init__(self, connector: DBConnector):
        self.connector = connector

    def create(self, item: ProductDTO, order_id: int, quantity: int):
        query = "INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES (?, ?, ?, ?)"
        self.connector.execute_query(query, (order_id, item.id, quantity, item.price))

    def get_by_order_id(self, order_id: int) -> List[Dict]:
        query = """
            SELECT oi.product_id, p.name, oi.quantity, oi.price_at_order
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """
        result = self.connector.execute_query(query, (order_id,))
        
        items = []
        if not result.empty:
            for _, row in result.iterrows():
                items.append({
                    "product_id": int(row['product_id']),
                    "product_name": row['name'],
                    "quantity": int(row['quantity']),
                    "price": float(row['price_at_order']),
                    "subtotal": int(row['quantity']) * float(row['price_at_order'])
                })
        return items

    def delete_by_order_id(self, order_id: int):
        self.connector.execute_query("DELETE FROM order_items WHERE order_id = ?", (order_id,))
