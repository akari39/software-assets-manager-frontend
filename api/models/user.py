from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from schemas.employee import EmployeeRead

if TYPE_CHECKING:
    from models.employee import Employee
    from models.licenses_usage_record import LicensesUsageRecord

class UserBase(SQLModel):
    employee_id: str = Field(
        index=True,
        unique=True,
        foreign_key="employees.employee_id",
        description="关联的员工工号"
    )
    permissions: int = Field(default=0, description="用户权限,0为普通用户, 1为管理员")
    status: int = Field(
        default=0,
        index=True,
        description="账号状态,0为正常, 1为禁用"
        )
    
class UserResponse(UserBase):
    user_id: int
    employee_id: str
    permissions: int
    status: int

class UserReadWithEmployee(UserResponse):
    employee: Optional[EmployeeRead] = None

class User(UserBase, table=True):
    user_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
        description="独立的用户主键ID"
    )

    hashed_password: str = Field()

    __tablename__ = "users" 

    '''
    licenses_usage_record: list["LicensesUsageRecord"] = Relationship(
        back_populates="user_id",
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )
    '''