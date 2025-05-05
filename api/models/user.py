from __future__ import annotations # For forward references in type hints

from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# Import Employee only for type checking
if TYPE_CHECKING:
    from employee import Employee

class UserBase(SQLModel):
    employee_id: str = Field(
        index=True,
        unique=True, # Ensure one user per employee
        description="关联的员工工号"
    )
    status: int = Field(default=0, index=True) # 用户状态 (例如: 0: 激活, 1: 禁用)

class User(UserBase, table=True):
    # --- New Primary Key ---
    user_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
        description="独立的用户主键ID"
    )
    # --- End New Primary Key ---

    hashed_password: str = Field()

    __tablename__ = "users" # Explicit table name