from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from api.dependencies import get_db_connector
from database.db_connector import DBConnector
from dao.user_dao import UserDAO
from models.user import UserDTO

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    registered_at: Optional[datetime]

@router.get("/", response_model=List[UserResponse])
def get_users(db: DBConnector = Depends(get_db_connector)):
    dao = UserDAO(db)
    return dao.get_all()

@router.post("/", response_model=int)
def create_user(user: UserCreate, db: DBConnector = Depends(get_db_connector)):
    dao = UserDAO(db)
    # Note: UserDTO might expect registered_at, handle defaults if needed
    user_dto = UserDTO(id=0, name=user.name, email=user.email, registered_at=datetime.now())
    try:
        return dao.create(user_dto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DBConnector = Depends(get_db_connector)):
    dao = UserDAO(db)
    user = dao.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
