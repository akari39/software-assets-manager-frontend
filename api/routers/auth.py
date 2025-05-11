# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from utils.jwt import create_access_token, verify_password
from models.user import User
from dependencies import get_session
from pydantic import BaseModel
from utils.jwt import get_current_user
from utils.PwdHash  import get_password_hash

router = APIRouter()

class LoginRequest(BaseModel):
    employee_id: str
    password: str

class RegisterRequest(BaseModel):
    employee_id: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/login")
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    # 查詢用戶是否存在
    result = await session.execute(
        select(User).where(User.employee_id == request.employee_id)
    )
    user = result.scalars().first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session)
):
    # 检查员工ID是否存在
    from models.employee import Employee
    employee = await session.get(Employee, request.employee_id)
    if not employee:
        raise HTTPException(status_code=400, detail="Employee does not exist")

    # 检查用户是否已存在
    result = await session.execute(
        select(User).where(User.employee_id == request.employee_id)
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # 创建新用户
    hashed_password = get_password_hash(request.password)
    new_user = User(employee_id=request.employee_id, hashed_password=hashed_password, status=0, permissions=0)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # 验证旧密码是否正确
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # 修改密码
    current_user.hashed_password = get_password_hash(request.new_password)
    session.add(current_user)
    await session.commit()

    return {"message": "Password changed successfully"}


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
