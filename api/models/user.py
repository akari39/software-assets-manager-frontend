from __future__ import annotations # For forward references in type hints
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# Import Employee only for type checking
if TYPE_CHECKING:
    from models.employee import Employee
    from models.licenses_usage_record import LicensesUsageRecord

class UserBase(SQLModel):
    employee_id: str = Field(
        index=True,
        unique=True, # Ensure one user per employee
        foreign_key="employees.employee_id",
        description="关联的员工工号"
    )
    permissions: int = Field(default=0) # 用户權限 (例如: 0: 用戶, 1: 管理員)
    status: int = Field(
        default=0,
        index=True
        ) # 用户状态 (例如: 0: 激活, 1: 禁用)

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

    employee: Optional["Employee"] = Relationship(back_populates="user")

    licenses_usage_record: list["LicensesUsageRecord"] = Relationship(
        back_populates="user_id",
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )