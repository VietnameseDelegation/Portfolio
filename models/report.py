from dataclasses import dataclass

@dataclass
class SummaryReportDTO:
    total_users: int
    total_orders: int
    total_revenue: float
    average_order_value: float
    top_selling_product: str
    top_selling_quantity: int
