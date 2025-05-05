# /schemas/user.py
from typing import Optional
from sqlmodel import SQLModel
from ..models.user import UserBase

# Schema for creating a user - requires employee_id and plain password
class UserCreate(UserBase):
    employee_id: str
    password: str # Plain password input

# Schema for reading user data - excludes password
class UserRead(UserBase):
    employee_id: str

# Schema for updating user data (e.g., status or password)
class UserUpdate(SQLModel):
    status: Optional[int] = None
    password: Optional[str] = None # Allow updating password