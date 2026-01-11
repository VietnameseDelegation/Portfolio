from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from api.dependencies import get_db_connector
from database.db_connector import DBConnector
from dao.order_dao import OrderDAO
from models.order import OrderDTO

router = APIRouter()

class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_date: Optional[datetime]
    status: str
    paid: bool

@router.get("/", response_model=List[OrderResponse])
def get_orders(db: DBConnector = Depends(get_db_connector)):
    dao = OrderDAO(db)
    return dao.get_all()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: DBConnector = Depends(get_db_connector)):
    dao = OrderDAO(db)
    order = dao.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
