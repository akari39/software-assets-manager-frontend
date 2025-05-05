# /routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError # To catch FK violations or PK duplicates
from typing import List, Optional

from dependencies import get_session #
from models.user import User
from models.employee import Employee # Need Employee to check if employee_id exists
from schemas.user import UserCreate, UserRead, UserUpdate
from dependencies import get_password_hash, verify_password # Import security utils

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
    创建新用户（关联到现有员工）。
    """
    # 1. Check if Employee exists
    employee = await session.get(Employee, user_in.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{user_in.employee_id}' not found. Cannot create user."
        )

    # 2. Check if User already exists for this employee
    existing_user = await session.get(User, user_in.employee_id)
    if existing_user:
         raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User account for employee ID '{user_in.employee_id}' already exists."
        )

    # 3. Hash the password
    hashed_password = get_password_hash(user_in.password)

    # 4. Create User object
    # Create a dict excluding the plain password and add the hashed one
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    db_user = User.model_validate(user_data)

    session.add(db_user)
    try:
        await session.commit()
        await session.refresh(db_user)
        # Create UserRead response manually to exclude password
        return UserRead.model_validate(db_user)
    except IntegrityError: # Catch potential race condition or other integrity issues
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User for employee ID '{user_in.employee_id}' may already exist or another integrity error occurred."
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/", response_model=List[UserRead])
async def read_users(
    status_filter: Optional[int] = Query(None, alias="status", description="按用户状态筛选 (例如: 0=激活, 1=禁用)"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(100, ge=1, le=200, description="每页数量"),
    session: AsyncSession = Depends(get_session)
):
    """
    获取用户列表，支持分页和按状态筛选。
    """
    offset = (page - 1) * limit
    query = select(User)

    if status_filter is not None:
        query = query.where(User.status == status_filter)

    result = await session.execute(
        query.offset(offset).limit(limit).order_by(User.employee_id)
    )
    users = result.scalars().all()
    # Convert to UserRead to ensure password isn't exposed
    return [UserRead.model_validate(user) for user in users]

# Get user by employee_id (which is the primary key for User)
@router.get("/{employee_id}", response_model=UserRead)
async def read_user_by_employee_id(
    employee_id: str, # ID is string
    session: AsyncSession = Depends(get_session)
):
    """
    根据工号 (用户主键) 获取单个用户信息。
    """
    db_user = await session.get(User, employee_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID '{employee_id}' not found"
        )
    # Convert to UserRead
    return UserRead.model_validate(db_user)

@router.put("/{employee_id}", response_model=UserRead)
async def update_user(
    employee_id: str, # ID is string
    user_in: UserUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    更新指定工号的用户信息（状态或密码）。
    """
    db_user = await session.get(User, employee_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID '{employee_id}' not found"
        )

    update_data = user_in.model_dump(exclude_unset=True)

    # Handle password update separately
    if "password" in update_data:
        new_password = update_data.pop("password") # Remove plain password from dict
        if new_password: # Only hash if a new password was provided
             db_user.hashed_password = get_password_hash(new_password)

    # Update other fields (like status)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    try:
        await session.commit()
        await session.refresh(db_user)
        # Convert to UserRead
        return UserRead.model_validate(db_user)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    employee_id: str, # ID is string
    session: AsyncSession = Depends(get_session)
):
    """
    根据工号删除用户记录。
    这仅删除用户账号，不会删除关联的员工记录。
    """
    db_user = await session.get(User, employee_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID '{employee_id}' not found"
        )

    await session.delete(db_user)
    try:
        await session.commit()
        return None # Return None for 204
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")