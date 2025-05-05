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
from security import get_password_hash, verify_password # Import security utils

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

    # 2. Check if User already exists for this employee_id (using select)
    # (Alternatively, rely on unique constraint in DB, caught by IntegrityError)
    query = select(User).where(User.employee_id == user_in.employee_id)
    existing_user_check = await session.execute(query)
    if existing_user_check.first():
         raise HTTPException(
             status_code=status.HTTP_409_CONFLICT,
             detail=f"User account for employee ID '{user_in.employee_id}' already exists."
         )

    # 3. Hash the password
    hashed_password = get_password_hash(user_in.password)

    # 4. Create User object
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    db_user = User.model_validate(user_data) # user_id will be None here

    session.add(db_user)
    try:
        await session.commit()
        await session.refresh(db_user) # Refresh to get the generated user_id
        return UserRead.model_validate(db_user) # Return using the Read schema
    except IntegrityError as e: # Catch unique constraint violation on employee_id
        await session.rollback()
        # Check if the error is due to the unique constraint on employee_id
        if "unique constraint" in str(e).lower() and "employee_id" in str(e).lower():
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User account for employee ID '{user_in.employee_id}' already exists."
            )
        # Handle other potential integrity errors (e.g., foreign key)
        raise HTTPException(status_code=500, detail=f"Database integrity error: {e}")
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
        query.offset(offset).limit(limit).order_by(User.user_id) # Order by new PK
    )
    users = result.scalars().all()
    return [UserRead.model_validate(user) for user in users]

# --- Get user by new primary key: user_id ---
@router.get("/{user_id}", response_model=UserRead)
async def read_user_by_id(
    user_id: int, # ID is now int
    session: AsyncSession = Depends(get_session)
):
    """
    根据用户主键 ID 获取单个用户信息。
    """
    # session.get uses the primary key
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return UserRead.model_validate(db_user)

# --- Optional: Keep or add endpoint to get user by employee_id ---
@router.get("/by_employee_id/{employee_id}", response_model=UserRead)
async def read_user_by_employee_id(
    employee_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    根据员工工号获取单个用户信息。
    """
    query = select(User).where(User.employee_id == employee_id)
    result = await session.execute(query)
    db_user = result.scalar_one_or_none() # Use scalar_one_or_none for unique field

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID '{employee_id}' not found"
        )
    return UserRead.model_validate(db_user)

# --- Update user by new primary key: user_id ---
@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int, # ID is now int
    user_in: UserUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    更新指定用户主键 ID 的用户信息（状态或密码）。
    """
    db_user = await session.get(User, user_id) # Fetch by new PK
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data:
        new_password = update_data.pop("password")
        if new_password:
             db_user.hashed_password = get_password_hash(new_password)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    try:
        await session.commit()
        await session.refresh(db_user)
        return UserRead.model_validate(db_user)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# --- Delete user by new primary key: user_id ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, # ID is now int
    session: AsyncSession = Depends(get_session)
):
    """
    根据用户主键 ID 删除用户记录。
    """
    db_user = await session.get(User, user_id) # Fetch by new PK
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