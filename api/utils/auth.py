# auth.py
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from security import verify_password
from dependencies import get_session

# 密钥和算法
SECRET_KEY = "your-secret-key"  # 建议使用环境变量配置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 验证用户登录
async def authenticate_user(session: AsyncSession, employee_id: str, password: str):
    user = await session.get(User, employee_id)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# 创建 JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id: str = payload.get("sub")
        if employee_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await session.get(User, employee_id)
    if user is None:
        raise credentials_exception
    return user

# 获取当前用户并检查权限
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.status != 0:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# 管理员权限检查
async def check_admin_permissions(current_user: User = Depends(get_current_user)):
    if current_user.permissions != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admin only")
    return current_user