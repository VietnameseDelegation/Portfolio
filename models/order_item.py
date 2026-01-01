from dataclasses import dataclass

@dataclass
class OrderItemDTO:
    order_id: int
    product_id: int
    quantity: int
    price_at_order: float
