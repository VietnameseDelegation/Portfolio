from database.db_connector import DBConnector
from models.report import SummaryReportDTO

class ReportDAO:
    def __init__(self, connector: DBConnector):
        self.connector = connector

    def get_summary_report(self) -> SummaryReportDTO:
        # 1. Total Users
        users_query = "SELECT COUNT(*) as count FROM users"
        users_result = self.connector.execute_query(users_query)
        total_users = int(users_result.iloc[0]['count']) if not users_result.empty else 0

        # 2. Total Orders
        orders_query = "SELECT COUNT(*) as count FROM orders"
        orders_result = self.connector.execute_query(orders_query)
        total_orders = int(orders_result.iloc[0]['count']) if not orders_result.empty else 0
        
        # 3. Revenue Stats (Total Revenue)
        revenue_query = """
            SELECT SUM(quantity * price_at_order) as total_revenue
            FROM order_items
        """
        revenue_result = self.connector.execute_query(revenue_query)
        total_revenue = float(revenue_result.iloc[0]['total_revenue']) if not revenue_result.empty and revenue_result.iloc[0]['total_revenue'] is not None else 0.0
        
        # 4. Average Order Value
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

        # 5. Top Selling Product (Max Quantity)
        top_product_query = """
            SELECT TOP 1 p.name, SUM(oi.quantity) as total_qty
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.name
            ORDER BY total_qty DESC
        """
        top_product_result = self.connector.execute_query(top_product_query)
        
        if not top_product_result.empty:
            top_row = top_product_result.iloc[0]
            top_selling_product = top_row['name']
            top_selling_quantity = int(top_row['total_qty'])
        else:
            top_selling_product = "None"
            top_selling_quantity = 0

        return SummaryReportDTO(
            total_users=total_users,
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_order_value=average_order_value,
            top_selling_product=top_selling_product,
            top_selling_quantity=top_selling_quantity
        )
