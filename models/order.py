from dataclasses import dataclass
from datetime import datetime

@dataclass
class OrderDTO:
    id: int
    user_id: int
    order_date: datetime
    status: str
    paid: bool
