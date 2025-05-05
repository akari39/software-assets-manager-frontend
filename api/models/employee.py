from __future__ import annotations # For forward references in type hints

from typing import Optional
from sqlmodel import SQLModel, Field

class EmployeeBase(SQLModel):
    name: str = Field(index=True)
    gender: int # 例如: 0: 未知, 1: 男, 2: 女
    department: Optional[str] = Field(default=None, index=True)
    level: int # 职级
    status: int = Field(default=0, index=True) # 状态 (例如: 0: 在职, 1: 离职)

class Employee(EmployeeBase, table=True):
    # 将 employee_id 作为主键，通常工号是唯一的字符串
    employee_id: str = Field(
        default=None,
        primary_key=True,
        index=True,
        unique=True,
        description="僱員工號")

    # Optional: Define the one-to-one relationship back to User
    # If an employee MUST have a user account, remove Optional.
    # If not all employees have user accounts, keep Optional.
    #user: Optional["User"] = Relationship(back_populates="employee")

    # Optional: Add a specific table name if needed
    __tablename__ = "employees"