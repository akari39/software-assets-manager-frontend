from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from utils.jwt import get_current_admin
from dependencies import get_session
from models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate


# 创建一个 APIRouter 实例，前缀为 /employees，用于管理员工相关的路由
router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

# 创建员工接口
@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_in: EmployeeCreate,
    session: AsyncSession = Depends(get_session)
):
    # 检查是否已存在相同 employee_id 的员工
    existing_employee = await session.get(Employee, employee_in.employee_id)
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"工号 '{employee_in.employee_id}' 已存在"
        )

    # 创建新员工实例并保存到数据库
    db_employee = Employee.model_validate(employee_in)
    session.add(db_employee)
    try:
        await session.commit()
        await session.refresh(db_employee)
        return db_employee
    except IntegrityError: 
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"工号 '{employee_in.employee_id}' 已存在或遇到数据一致性错误"
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")

# 获取所有员工列表，支持按部门、状态分页查询
@router.get("/", response_model=List[EmployeeRead])
async def read_employees(
    department: Optional[str] = Query(None, description="按部门筛选"),
    status: Optional[int] = Query(None, description="按状态筛选 (例如: 0=在职, 1=离职)"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(100, ge=1, le=200, description="每页数量"),
    session: AsyncSession = Depends(get_session)
):
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

# 根据 employee_id 获取特定员工信息
@router.get("/{employee_id}", response_model=EmployeeRead)
async def read_employee(
    employee_id: str,
    session: AsyncSession = Depends(get_session)
):
    db_employee = await session.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工号 '{employee_id}' 不存在"
        )
    return db_employee

# 更新指定 employee_id 的员工信息
@router.put("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: str,
    employee_in: EmployeeUpdate,
    session: AsyncSession = Depends(get_session)
):
    db_employee = await session.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工号 '{employee_id}' 不存在"
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
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")

# 删除指定 employee_id 的员工
@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=Depends(get_current_admin))
async def delete_employee(
    employee_id: str, 
    session: AsyncSession = Depends(get_session)
):
    db_employee = await session.get(Employee, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工号 '{employee_id}' 不存在"
        )

    await session.delete(db_employee)
    try:
        await session.commit()
        return None
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"无法删除用户，有关联的数据存在 Error: {e}")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")