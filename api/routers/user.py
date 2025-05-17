from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from dependencies import get_session
from models.user import User, UserReadWithEmployee
from models.employee import Employee
from schemas.user import UserCreate, UserRead, UserUpdate
from schemas.employee import EmployeeRead
from utils.PwdHash import get_password_hash, verify_password

# 创建一个API路由实例，前缀为 "/users"，标签为 "Users"
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    创建新用户。
    
    参数:
        user_in (UserCreate): 用户创建请求体。
        session (AsyncSession): 数据库会话。

    返回:
        UserRead: 创建成功的用户信息。
    """
    # 根据提供的 employee_id 查询员工是否存在
    if user_in.employee is not None:
        existing_employee_check = await session.get(Employee, user_in.employee.employee_id)
        if existing_employee_check:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with ID '{user_in.employee.employee_id}' already exists."
            )
        db_employee = Employee.model_validate(user_in.employee)
        session.add(db_employee)
        try:
            await session.commit()
            await session.refresh(db_employee)
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating employee: {str(e)}"
            )
    
    else:
        employee = await session.get(Employee, user_in.employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{user_in.employee_id}' not found. Cannot create user."
            )

    # 检查是否已经存在相同 employee_id 的用户
    query = select(User).where(User.employee_id == user_in.employee_id)
    existing_user_check = await session.execute(query)
    if existing_user_check.first():
         raise HTTPException(
             status_code=status.HTTP_409_CONFLICT,
             detail=f"User account for employee ID '{user_in.employee_id}' already exists."
         )

    # 对密码进行哈希处理
    hashed_password = get_password_hash(user_in.password)

    # 构建用户数据并排除密码字段
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    db_user = User.model_validate(user_data)

    # 将新用户添加到数据库
    session.add(db_user)
    try:
        await session.commit()
        await session.refresh(db_user)
        return UserRead.model_validate(db_user)
    except IntegrityError as e:
        await session.rollback()
        if "unique constraint" in str(e).lower() and "employee_id" in str(e).lower():
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User account for employee ID '{user_in.employee_id}' already exists."
            )
        raise HTTPException(status_code=500, detail=f"Database integrity error: {e}")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/", response_model=List[UserReadWithEmployee])
async def read_users(
    status_filter: Optional[int] = Query(None, alias="status", description="按用户状态筛选 (例如: 0=激活, 1=禁用)"),
    permissions_filter: Optional[int] = Query(None, alias="permissions", description="按用户權限筛选 (例如: 0=用戶, 1=管理員)"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(100, ge=1, le=200, description="每页数量"),
    session: AsyncSession = Depends(get_session)
):
    """
    获取所有用户列表（支持分页和筛选）。
    
    参数:
        status_filter (Optional[int]): 可选的状态筛选。
        permissions_filter (Optional[int]): 可选的权限筛选。
        page (int): 当前页码。
        limit (int): 每页的最大记录数。
        session (AsyncSession): 数据库会话。

    返回:
        List[UserRead]: 当前页的用户列表。
    """
    offset = (page - 1) * limit
    query = (
        select(User, Employee)
        .join(Employee, User.employee_id == Employee.employee_id)
        )

    # 应用状态筛选条件
    if status_filter is not None:
        query = query.where(User.status == status_filter)

    # 应用权限筛选条件
    if permissions_filter is not None:
        query = query.where(User.permissions == permissions_filter)

    # 执行查询并进行分页
    result = await session.execute(
        query.offset(offset).limit(limit).order_by(User.user_id)
    )
    users_with_employees = result.all()
    return [
            UserReadWithEmployee(
                user_id=user.user_id,
                employee_id=user.employee_id,
                permissions=user.permissions,
                status=user.status,
                employee=EmployeeRead.model_validate(employee)
            )
            for user, employee in users_with_employees
        ]

@router.get("/{user_id}", response_model=UserReadWithEmployee)
async def read_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    根据用户ID获取用户详情。
    
    参数:
        user_id (int): 用户的唯一标识。
        session (AsyncSession): 数据库会话。

    返回:
        UserRead: 用户详细信息。
    """
    result = await session.execute(
        select(User, Employee).join(Employee).where(User.user_id == user_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user, employee = row
    return UserReadWithEmployee(
        user_id=user.user_id,
        employee_id=user.employee_id,
        permissions=user.permissions,
        status=user.status,
        employee=EmployeeRead.model_validate(employee)
    )

@router.get("/by_employee_id/{employee_id}", response_model=UserReadWithEmployee)
async def read_user_by_employee_id(
    employee_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    根据员工ID获取用户详情。
    
    参数:
        employee_id (str): 员工的唯一标识。
        session (AsyncSession): 数据库会话。

    返回:
        UserRead: 用户详细信息。
    """
    result = await session.execute(
        select(User, Employee).join(Employee).where(User.employee_id == employee_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID '{employee_id}' not found"
        )

    user, employee = row

    return UserReadWithEmployee(
        user_id=user.user_id,
        employee_id=user.employee_id,
        permissions=user.permissions,
        status=user.status,
        employee=EmployeeRead.model_validate(employee)
    )

@router.get("/search", response_model=List[UserReadWithEmployee])
async def search_users(
    search_type: str = Query(..., description="搜索类型 (name|employee_id)"),
    search_value: str = Query(..., description="搜索值"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_session)
):
    offset = (page - 1) * limit
    query = select(User, Employee).join(Employee)

    # 根据搜索类型构建过滤条件
    if search_type == "name":
        query = query.where(Employee.name.ilike(f"%{search_value}%"))
    elif search_type == "employee_id":
        query = query.where(Employee.employee_id.ilike(f"%{search_value}%"))
    else:
        raise HTTPException(status_code=400, detail="无效的搜索类型。支持 'name' 或 'employee_id'")

    # 分页处理
    result = await session.execute(query.offset(offset).limit(limit).order_by(User.user_id))
    users_with_employees = result.all()

    return [
        UserReadWithEmployee(
            user_id=user.user_id,
            employee_id=user.employee_id,
            permissions=user.permissions,
            status=user.status,
            employee=EmployeeRead.model_validate(employee)
        )
        for user, employee in users_with_employees
    ]

@router.put("/{user_id}", response_model=UserReadWithEmployee)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    更新指定用户的信息。
    
    参数:
        user_id (int): 用户的唯一标识。
        user_in (UserUpdate): 包含更新数据的请求体。
        session (AsyncSession): 数据库会话。

    返回:
        UserRead: 更新后的用户信息。
    """
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    db_employee = await session.get(Employee, db_user.employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=404,
            detail="Associated employee not found"
        )

    update_data = user_in.model_dump(exclude_unset=True)

    # 如果有新的密码，则进行哈希处理
    if "password" in update_data:
        new_password = update_data.pop("password")
        if new_password:
             db_user.hashed_password = get_password_hash(new_password)

    employee_update = update_data.pop("employee", None)

    # 更新其他字段
    for key, value in update_data.items():
        setattr(db_user, key, value)

    if employee_update:
        for key, value in employee_update.items():
            setattr(db_employee, key, value)
        session.add(db_employee)

    session.add(db_user)

    try:
        await session.commit()
        await session.refresh(db_user)
        await session.refresh(db_employee)

        return UserReadWithEmployee(
            user_id=db_user.user_id,
            employee_id=db_user.employee_id,
            permissions=db_user.permissions,
            status=db_user.status,
            employee=EmployeeRead.model_validate(db_employee)
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    删除指定用户。
    
    参数:
        user_id (int): 用户的唯一标识。
        session (AsyncSession): 数据库会话。

    返回:
        None.
    """
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    await session.delete(db_user)
    try:
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")