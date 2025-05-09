# utils/jwt.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from dependencies import get_session
from schemas.user import UserRead
from passlib.context import CryptContext
import os


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "SECRET_KEY_FOR_NON_ENVIRONMENT_FALLBACK_USE_ONLY_DO_NOT_USE_IN_PRODUCTION_CWNUICBIEWFBUIFBCEUOBCEOUBCEUIOBCIOUEBWOUCBWOUCH89023UIO24NF8927HF0"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        try:
            user_id: int = int(user_id_str)
        except (TypeError, ValueError):
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    user = await get_current_user(token, session)  # 先取得當前用戶
    if user.permissions != 1:  # 假設 1 表示管理員
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted - Admin access required"
        )
    return user
