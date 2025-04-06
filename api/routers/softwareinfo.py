from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Optional, AsyncGenerator

# 定義數據模型 (只在路由文件內部使用)
class SoftwareBase(SQLModel):
    SoftwareName: str = Field(min_length=1)
    SoftwareType: Optional[int] = None
    SoftwareMatchRule: Optional[str] = None
    
class Software(SoftwareBase, table=True):
    __tablename__ = "software_info" 
    SoftwareID: Optional[int] = Field(default=None, primary_key=True)

# 請求/響應模型
class SoftwareCreate(SoftwareBase):
    pass

class SoftwareRead(SoftwareBase):
    SoftwareID: int

class SoftwareUpdate(SQLModel):
    SoftwareName: Optional[str] = None
    SoftwareType: Optional[int] = None
    SoftwareMatchRule: Optional[str] = None

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

# 路由處理函數
@router.post("/", response_model=SoftwareRead, status_code=status.HTTP_201_CREATED)
async def create_software(
    software: SoftwareCreate,
    session: AsyncSession = Depends(get_session)
):
    db_software = Software.model_validate(software)
    session.add(db_software)
    await session.commit()
    await session.refresh(db_software)
    return db_software
