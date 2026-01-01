from typing import List, Optional, Dict, Any
from datetime import datetime
from models.user import UserDTO
from models.product import ProductDTO
from database.db_connector import DBConnector

class OrderDAO:
    def __init__(self, connector: DBConnector):
        self.connector = connector

    def create_full_order(self, user: UserDTO, status: str, items: List[ProductDTO], quantities: List[int]) -> int:
        """
        Creates an order with user and items.
        Returns the new Order ID.
        """
        if len(items) != len(quantities):
            raise ValueError("Items and quantities must have the same length")

        # 1. Handle User (Find or Create)
        user_df = self.connector.execute_query("SELECT id FROM users WHERE email = ?", (user.email,))
        
        if not user_df.empty:
            user_id = int(user_df.iloc[0]['id'])
        else:
            # SQL Server: OUTPUT INSERTED.ID is better, or SELECT SCOPE_IDENTITY()
            # Using SELECT SCOPE_IDENTITY() as a second statement in the same batch
            insert_user_query = "INSERT INTO users (name, email, registered_at) VALUES (?, ?, ?); SELECT SCOPE_IDENTITY() AS id;"
            user_result = self.connector.execute_query(insert_user_query, (user.name, user.email, user.registered_at))
            user_id = int(user_result.iloc[0]['id'])
        
        # 2. Insert Order
        insert_order_query = "INSERT INTO orders (user_id, order_date, status, paid) VALUES (?, ?, ?, ?); SELECT SCOPE_IDENTITY() AS id;"
        # datetime.now() formatting might be needed or handled by driver. 
        # pyodbc handles datetime objects usually.
        order_result = self.connector.execute_query(insert_order_query, (user_id, datetime.now(), status, False))
        order_id = int(order_result.iloc[0]['id'])
        
        # 3. Insert Order Items
        for item, qty in zip(items, quantities):
            self.connector.execute_query(
                "INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES (?, ?, ?, ?)",
                (order_id, item.id, qty, item.price)
            )
        
        return order_id

    def get_order_with_details(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves order details including user and items.
        """
        # Get Order and User info
        query_order = """
            SELECT o.id, o.order_date, o.status, o.paid, 
                   u.id as user_id, u.name as user_name, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = ?
        """
        order_df = self.connector.execute_query(query_order, (order_id,))
        
        if order_df.empty:
            return None
        
        order_row = order_df.iloc[0]
        
        result = {
            "order_id": int(order_row['id']),
            # Handle potential pandas Timestamp conversion if needed, but pyodbc+pandas usually behaves
            "order_date": order_row['order_date'],
            "status": order_row['status'],
            "paid": bool(order_row['paid']),
            "user": {
                "id": int(order_row['user_id']),
                "name": order_row['user_name'],
                "email": order_row['email']
            },
            "items": []
        }
        
        # Get Items
        query_items = """
            SELECT oi.product_id, p.name, oi.quantity, oi.price_at_order
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """
        items_df = self.connector.execute_query(query_items, (order_id,))
        
        if not items_df.empty:
            for _, row in items_df.iterrows():
                result["items"].append({
                    "product_id": int(row['product_id']),
                    "product_name": row['name'],
                    "quantity": int(row['quantity']),
                    "price": float(row['price_at_order']),
                    "subtotal": int(row['quantity']) * float(row['price_at_order'])
                })
            
        return result

    def update_order_status(self, order_id: int, new_status: str):
        self.connector.execute_query("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))

    def delete_order(self, order_id: int):
        """
        Deletes an order and its items.
        """
        # Delete items first
        self.connector.execute_query("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        
        # Delete order
        self.connector.execute_query("DELETE FROM orders WHERE id = ?", (order_id,))
