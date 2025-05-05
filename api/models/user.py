from __future__ import annotations # For forward references in type hints

from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# Import Employee only for type checking
if TYPE_CHECKING:
    from .employee import Employee

class UserBase(SQLModel):
    # employee_id is defined in the main User class as it's the PK/FK
    status: int = Field(default=0, index=True) # 用户状态 (例如: 0: 激活, 1: 禁用)

class User(UserBase, table=True):
    employee_id: str = Field(
        default=None,
        foreign_key="employee.employee_id", # Links to Employee table's employee_id
        primary_key=True,
        index=True,
        description="关联的员工工号，同时作为用户主键"
    )
    hashed_password: str = Field()

    # Define the one-to-one relationship to Employee
    employee: "Employee" = Relationship(back_populates="user")

    __tablename__ = "users" # Explicit table name