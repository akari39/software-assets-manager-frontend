# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from utils.jwt import create_access_token, verify_password
from models.user import User
from dependencies import get_session
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    employee_id: str
    password: str

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