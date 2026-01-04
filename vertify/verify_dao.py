import sys
import os
# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from models.user import UserDTO
from models.product import ProductDTO
from dao.order_dao import OrderDAO
from config.config_processor import ConfigProcessor
from database.db_connector import DBConnector
import time

def verify_dao():
    print("Initializing components...")
    try:
        config = ConfigProcessor("config.ini")
        connector = DBConnector(config)
        dao = OrderDAO(connector)
    except Exception as e:
        print(f"Failed to init DB connection. Ensure DB is running and config is correct. Error: {e}")
        return

    print("Components initialized.")

    # 1. Prepare Data
    timestamp = int(time.time())
    user_email = f"user_{timestamp}@example.com"
    
    user = UserDTO(id=0, name="DAO Tester", email=user_email, registered_at=datetime.now())
    
    # Insert Test Data (Category + Product) manually if needed or assume existence.
    # We'll try to use existing or creating new ones.
    # Note: Using connector.execute_query now as we refactored.
    
    print("Preparing test product...")
    try:
        # Create Category
        cat_query = "INSERT INTO categories (name) VALUES ('TestCat'); SELECT SCOPE_IDENTITY() as id;"
        cat_df = connector.execute_query(cat_query)
        cat_id = int(cat_df.iloc[0]['id'])
        
        # Create Product
        prod_query = "INSERT INTO products (name, price, category_id, active) VALUES ('TestProduct', 50.0, ?, 1); SELECT SCOPE_IDENTITY() as id;"
        prod_df = connector.execute_query(prod_query, (cat_id,))
        prod_id = int(prod_df.iloc[0]['id'])
        
        product1 = ProductDTO(id=prod_id, name="TestProduct", price=50.0, category_id=cat_id, active=True)
    except Exception as e:
        print(f"Failed to prepare test data: {e}")
        return

    # 2. Create Order
    print(f"Creating order for {user.email}...")
    try:
        order_id = dao.create_full_order(user, "new", [product1], [2])
        print(f"Order created with ID: {order_id}")
    except Exception as e:
        print(f"Failed to create order: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Get Order Details
    print("Fetching order details...")
    details = dao.get_order_with_details(order_id)
    print(f"Details: {details}")
    
    if details['user']['email'] != user_email:
        print("ERROR: User email mismatch")
    if len(details['items']) != 1:
        print("ERROR: Item count mismatch")
    # Subtotal check: 2 * 50.0 = 100.0
    if details['items'][0]['subtotal'] != 100.0:
        print(f"ERROR: Subtotal calculation mismatch. Expected 100.0, got {details['items'][0]['subtotal']}")

    # 4. Update Status
    print("Updating status to 'paid'...")
    dao.update_order_status(order_id, "paid")
    
    details_updated = dao.get_order_with_details(order_id)
    print(f"New Status: {details_updated['status']}")
    if details_updated['status'] != 'paid':
         print("ERROR: Status update failed")

    # 5. Delete Order
    print("Deleting order...")
    dao.delete_order(order_id)
    
    details_deleted = dao.get_order_with_details(order_id)
    if details_deleted is None:
        print("Order deleted successfully.")
    else:
        print("ERROR: Order still exists")

    print("Verification complete.")

if __name__ == "__main__":
    verify_dao()
