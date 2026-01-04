from typing import Optional
from datetime import datetime
from database.db_connector import DBConnector
from models.order import OrderDTO

class OrderDAO:
    def __init__(self, connector: DBConnector):
        self.connector = connector

    def create(self, order: OrderDTO) -> int:
        query = "INSERT INTO orders (user_id, order_date, status, paid) VALUES (?, ?, ?, ?); SELECT SCOPE_IDENTITY() AS id;"
        result = self.connector.execute_query(query, (order.user_id, order.order_date, order.status, order.paid))
        return int(result.iloc[0]['id'])  

    def get_by_id(self, order_id: int) -> Optional[OrderDTO]:
        query = "SELECT id, user_id, order_date, status, paid FROM orders WHERE id = ?"
        result = self.connector.execute_query(query, (order_id,))
        
        if result.empty:
            return None
            
        row = result.iloc[0]
        return OrderDTO(
            id=int(row['id']),
            user_id=int(row['user_id']),
            order_date=row['order_date'],
            status=row['status'],
            paid=bool(row['paid'])
        )

    def update_status(self, order_id: int, new_status: str):
        self.connector.execute_query("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))

    def delete(self, order_id: int):
        self.connector.execute_query("DELETE FROM orders WHERE id = ?", (order_id,))
