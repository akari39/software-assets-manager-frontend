from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError # To catch unique constraint violations
from typing import List, Optional

from ..dependencies import get_session # Assuming get_session is in dependencies.py
from ..models.employee import Employee
from ..schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_in: EmployeeCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    创建新员工记录。
    """
    # Check if employee_id already exists (optional but good practice)
    existing_employee = await session.get(Employee, employee_in.employee_id)
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with ID '{employee_in.employee_id}' already exists."
        )

    db_employee = Employee.model_validate(employee_in)
    session.add(db_employee)
    try:
        await session.commit()
        await session.refresh(db_employee)
        return db_employee
    except IntegrityError: # Catch potential race condition for unique employee_id
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with ID '{employee_in.employee_id}' already exists or another integrity error occurred."
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.get("/", response_model=List[EmployeeRead])
async def read_employees(
    department: Optional[str] = Query(None, description="按部门筛选"),
    status: Optional[int] = Query(None, description="按状态筛选 (例如: 0=在职, 1=离职)"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(100, ge=1, le=200, description="每页数量"), # Increased default limit
    session: AsyncSession = Depends(get_session)
):
    """
    获取员工列表，支持分页和筛选。
    """
    offset = (page - 1) * limit
    query = select(Employee)

    if department is not None:
        query = query.where(Employee.department == department)
    if status is not None:
        query = query.where(Employee.status == status)

    result = await session.execute(
        query.offset(offset).limit(limit).order_by(Employee.employee_id) # Order by ID
    )
    employees = result.scalars().all()
    return employees

@router.get("/{employee_id}", response_model=EmployeeRead)
async def read_employee(
    employee_id: str, # ID is string
    session: AsyncSession = Depends(get_session)
):
    """
    根据工号获取单个员工信息。
    """
    db_employee = await session.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found"
        )
    return db_employee

@router.put("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: str, # ID is string
    employee_in: EmployeeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    更新指定工号的员工信息。
    """
    db_employee = await session.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found"
        )

    update_data = employee_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)

    session.add(db_employee)
    try:
        await session.commit()
        await session.refresh(db_employee)
        return db_employee
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str, # ID is string
    session: AsyncSession = Depends(get_session)
):
    """
    根据工号删除员工记录。
    注意：这会硬删除记录。考虑是否需要软删除（更新状态）。
    同时需要考虑关联的 User 记录如何处理（级联删除或禁止删除）。
    """
    db_employee = await session.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found"
        )

    # Add check for related User if necessary before deleting
    # if db_employee.user:
    #     raise HTTPException(status_code=400, detail="Cannot delete employee with an active user account.")

    await session.delete(db_employee)
    try:
        await session.commit()
        return None # Return None for 204
    except IntegrityError as e:
        # Handle cases where deletion is blocked by foreign key constraints
        # (e.g., if User table has a foreign key constraint without ON DELETE CASCADE)
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete employee. Check related records (e.g., user accounts). Error: {e}")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")