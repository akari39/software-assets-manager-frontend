# 导入必要的模块和工具
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from utils.jwt import create_access_token, verify_password
from models.user import User, UserResponse, UserReadWithEmployee
from dependencies import get_session
from pydantic import BaseModel
from utils.jwt import get_current_user
from utils.PwdHash import get_password_hash

# 创建一个API路由实例
router = APIRouter(
    tags= ["Auth"]
)

# 定义登录请求的数据模型
class LoginRequest(BaseModel):
    employee_id: str
    password: str

# 定义注册请求的数据模型
class RegisterRequest(BaseModel):
    employee_id: str
    password: str

# 定义修改密码请求的数据模型
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# 登录接口，用于验证用户并生成访问令牌
@router.post("/login")
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    # 查询用户是否存在
    result = await session.execute(
        select(User).where(User.employee_id == request.employee_id)
    )
    user = result.scalars().first()

    # 如果用户不存在或密码不正确，抛出异常
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="错误的工号或密码")

    # 生成访问令牌
    access_token = create_access_token(data={"sub": str(user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}

# 注册接口，用于创建新用户
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session)
):
    from models.employee import Employee
    # 检查员工是否存在
    employee = await session.get(Employee, request.employee_id)
    if not employee:
        raise HTTPException(status_code=400, detail="工号不存在")

    # 检查员工是否已经存在用户
    result = await session.execute(
        select(User).where(User.employee_id == request.employee_id)
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户已注册")

    # 哈希密码并创建新用户
    hashed_password = get_password_hash(request.password)
    new_user = User(employee_id=request.employee_id, hashed_password=hashed_password, status=0, permissions=0)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"message": "注册成功"}

# 修改密码接口，仅允许已登录用户修改自己的密码
@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # 验证旧密码是否正确
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="旧密码不正确")

    # 更新密码
    current_user.hashed_password = get_password_hash(request.new_password)
    session.add(current_user)
    await session.commit()

    return {"message": "更改成功"}

# 获取当前用户信息的接口
@router.get("/me", response_model=UserReadWithEmployee)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user