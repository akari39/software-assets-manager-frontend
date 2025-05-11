from typing import Optional
from sqlmodel import SQLModel
from models.employee import EmployeeBase

class EmployeeCreate(EmployeeBase):
    employee_id: str # 创建时必须提供工号

class EmployeeRead(EmployeeBase):
    employee_id: str

class EmployeeUpdate(SQLModel):
    name: Optional[str] = None
    gender: Optional[int] = None
    department: Optional[str] = None
    level: Optional[int] = None
    status: Optional[int] = None