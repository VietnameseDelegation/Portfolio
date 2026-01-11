from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from api.dependencies import get_db_connector
from database.db_connector import DBConnector
from dao.product_dao import ProductDAO
from models.product import ProductDTO

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    price: float
    category_id: int
    active: bool = True

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category_id: int
    active: bool

@router.post("/", response_model=int)
def create_product(product: ProductCreate, db: DBConnector = Depends(get_db_connector)):
    dao = ProductDAO(db)
    # ID is 0 placeholder, actual ID returned by DB
    product_dto = ProductDTO(id=0, name=product.name, price=product.price, category_id=product.category_id, active=product.active)
    try:
        return dao.create(product_dto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ProductResponse])
def get_products(db: DBConnector = Depends(get_db_connector)):
    dao = ProductDAO(db)
    return dao.get_all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: DBConnector = Depends(get_db_connector)):
    dao = ProductDAO(db)
    product = dao.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
