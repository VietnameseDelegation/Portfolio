from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserDTO:
    id: int
    name: str
    email: str
    registered_at: datetime
