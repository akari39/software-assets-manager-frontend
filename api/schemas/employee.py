from typing import Optional
from sqlmodel import SQLModel
from ..models.employee import EmployeeBase

# Schema for creating an employee (usually doesn't include the ID if it's generated)
# Since employee_id is the primary key AND provided externally (工号), include it here.
class EmployeeCreate(EmployeeBase):
    employee_id: str # 创建时必须提供工号

# Schema for reading employee data (includes the ID)
class EmployeeRead(EmployeeBase):
    employee_id: str

# Schema for updating an employee (all fields optional)
class EmployeeUpdate(SQLModel):
    name: Optional[str] = None
    gender: Optional[int] = None
    department: Optional[str] = None
    level: Optional[int] = None
    status: Optional[int] = None