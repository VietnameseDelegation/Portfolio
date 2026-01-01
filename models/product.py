from dataclasses import dataclass

@dataclass
class ProductDTO:
    id: int
    name: str
    price: float
    category_id: int
    active: bool
