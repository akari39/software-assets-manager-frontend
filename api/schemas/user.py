from typing import Optional
from sqlmodel import SQLModel
from models.user import UserBase
from schemas.employee import EmployeeUpdate

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    user_id: int

class UserUpdate(SQLModel):
    status: Optional[int] = None
    permissions: Optional[int] = None
    password: Optional[str] = None
    employee: Optional[EmployeeUpdate] = None
