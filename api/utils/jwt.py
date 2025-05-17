# utils/jwt.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.employee import EmployeeRead
from models.user import User, UserReadWithEmployee
from models.employee import Employee
from dependencies import get_session
from passlib.context import CryptContext
import os

# 使用 OAuth2 的 Bearer Token 认证方式，指定获取 token 的 URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# 从环境变量中获取密钥，若未设置则使用默认值（仅用于开发环境）
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "SECRET_KEY_FOR_NON_ENVIRONMENT_FALLBACK_USE_ONLY_DO_NOT_USE_IN_PRODUCTION_CWNUICBIEWFBUIFBCEUOBCEOUBCEUIOBCIOUEBWOUCBWOUCH89023UIO24NF8927HF0"
)

# 指定 JWT 加密算法
ALGORITHM = "HS256"

# 设置访问令牌的过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码加密上下文，使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配
    :param plain_password: 明文密码
    :param hashed_password: 哈希后的密码
    :return: 匹配结果（True/False）
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    将明文密码哈希化
    :param password: 明文密码
    :return: 哈希后的密码
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建 JWT 访问令牌
    :param data: 要编码的数据（通常是用户信息）
    :param expires_delta: 自定义过期时间
    :return: 编码后的 JWT 令牌
    """
    to_encode = data.copy()
    # 如果提供了过期时间，则使用该时间，否则默认为15分钟
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=180)
    to_encode.update({"exp": expire})  # 添加过期时间字段
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # 编码 JWT
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    根据 token 获取当前用户
    :param token: Bearer Token
    :param session: 数据库会话
    :return: 当前用户对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",  # 凭证验证失败提示
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        user_id_str: Optional[str] = payload.get("sub")  # 提取用户 ID 字符串
        if user_id_str is None:
            raise credentials_exception  # 用户 ID 不存在则抛出异常
        try:
            user_id: int = int(user_id_str)  # 尝试将字符串转为整数
        except (TypeError, ValueError):
            raise credentials_exception  # 转换失败也抛出异常
    except JWTError:
        raise credentials_exception  # JWT 解码失败时抛出异常

    # 查询数据库中的用户
    query = select(User, Employee).join(Employee)
    if user_id:
        query = query.where(User.user_id == user_id)
    result = await session.execute(query)
    row = result.first()
    #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"+row)
    if not row:
        raise credentials_exception  # 用户不存在则抛出异常
    
    user, employee = row
    
    return UserReadWithEmployee(
        user_id=user.user_id,
        employee_id=user.employee_id,
        permissions=user.permissions,
        status=user.status,
        employee=EmployeeRead.model_validate(employee)
    )

async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    获取当前管理员用户
    :param token: Bearer Token
    :param session: 数据库会话
    :return: 管理员用户对象
    """
    user = await get_current_user(token, session)  # 获取当前用户

    if user.permissions != 1:  # 权限判断（1 表示管理员权限）
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted - Admin access required"  # 非管理员无权限操作
        )
    return user