from dataclasses import dataclass
from datetime import datetime

@dataclass
class PaymentDTO:
    id: int
    order_id: int
    amount: float
    payment_date: datetime
    method: str
