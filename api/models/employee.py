from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from models.user import User

class EmployeeBase(SQLModel):
    name: str = Field(index=True, description="姓名")
    gender: int = Field(default=0, index=True, description="0为其他, 1为男, 2为女")
    department: Optional[str] = Field(default=None, index=True, description="部门名称")
    level: int = Field(default=1, index=True, description="范围0-5")
    status: int = Field(default=0, index=True, description="0为在职, 1为离职,2为停用")

class Employee(EmployeeBase, table=True):
    employee_id: str = Field(
        default=None,
        primary_key=True,
        index=True,
        unique=True,
        description="工号")

    __tablename__ = "employees"
    '''
    user: Optional["User"] = Relationship(
        back_populates="employee", # 指向 User.employee
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    '''
