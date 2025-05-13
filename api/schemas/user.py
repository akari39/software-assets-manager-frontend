from typing import Optional
from sqlmodel import SQLModel
from models.user import UserBase

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    user_id: int

class UserUpdate(SQLModel):
    status: Optional[int] = None
    permissions: Optional[int] = None
    password: Optional[str] = None