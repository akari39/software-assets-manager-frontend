from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select, create_engine, Field
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

# 使用 asyncpg
DATABASE_URL = "postgresql+asyncpg://postgres:huiji.233@localhost:5432/dev"
engine = create_async_engine(DATABASE_URL, echo=True)

# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 依赖项：获取数据库会话
async def get_session():
    # 使用上下文管理器确保会话正确关闭
    async with AsyncSessionLocal() as session:
        yield session  # 生成器方式提供会话

class SoftwareBase(SQLModel):
    SoftwareName: str = Field(min_length=1)
    SoftwareType: Optional[int] = None
    SoftwareMatchRule: Optional[str] = None
    
class Software(SoftwareBase, table=True):
    __tablename__ = "software_info" 
    SoftwareID: Optional[int] = Field(default=None, primary_key=True)

class SoftwareCreate(SoftwareBase):
    pass

class SoftwareRead(SoftwareBase):
    SoftwareID: int

class SoftwareUpdate(SQLModel):
    SoftwareName: Optional[str] = None
    SoftwareType: Optional[int] = None
    SoftwareMatchRule: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/software/", response_model=SoftwareRead, status_code=status.HTTP_201_CREATED)
async def create_software(
    software: SoftwareCreate,          # 请求体参数（自动验证）
    session: AsyncSession = Depends(get_session)  # 注入数据库会话
):
    # 将请求数据转换为数据库模型
    db_software = Software.model_validate(software)
    # 添加到会话
    session.add(db_software)
    # 提交事务
    await session.commit()
    # 刷新对象以获取数据库生成的ID等数据
    await session.refresh(db_software)
    return db_software