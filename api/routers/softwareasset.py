from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, SQLModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, AsyncGenerator

# 定義數據模型 (只在路由文件內部使用)
class SoftwareInfoBase(SQLModel):
    SoftwareInfoName: str = Field(min_length=1)
    SoftwareInfoType: Optional[int] = None
    SoftwareInfoMatchRule: Optional[str] = None
    
class SoftwareInfo(SoftwareInfoBase, table=True):
    __tablename__ = "software_info" 
    SoftwareInfoID: Optional[int] = Field(default=None, primary_key=True)

# 請求/響應模型
class SoftwareInfoCreate(SoftwareInfoBase):
    pass

class SoftwareInfoRead(SoftwareInfoBase):
    SoftwareInfoID: int

class SoftwareInfoUpdate(SQLModel):
    SoftwareInfoName: Optional[str] = None
    SoftwareInfoType: Optional[int] = None
    SoftwareInfoMatchRule: Optional[str] = None

# 創建路由實例
router = APIRouter(
    prefix="/softwareinfo",
    tags=["softwareinfo"]
)

# 依賴注入 (內部定義)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    from main import engine
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session