# /schemas/user.py
from typing import Optional
from sqlmodel import SQLModel
from models.user import UserBase # Now includes employee_id

# Schema for creating a user - requires employee_id and plain password
# Inherits employee_id from UserBase now
class UserCreate(UserBase):
    password: str # Plain password input

# Schema for reading user data - includes the new user_id
class UserRead(UserBase):
    user_id: int # Include the new primary key

# Schema for updating user data (e.g., status or password)
class UserUpdate(SQLModel):
    status: Optional[int] = None
    password: Optional[str] = None # Allow updating password
    # employee_id is generally not updated once set.