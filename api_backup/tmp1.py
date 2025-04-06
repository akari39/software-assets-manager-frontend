from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, select, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

app = FastAPI()

# 异步引擎
DATABASE_URL = "postgresql+asyncpg://postgres:huiji.233@localhost:5432/dev"
engine = create_async_engine(DATABASE_URL, echo=True)

# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 依赖项
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# 模型定义
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

# 生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

# 路由
@app.post("/software/", response_model=SoftwareRead, status_code=201)
async def create_software(
    software: SoftwareCreate,
    session: AsyncSession = Depends(get_session)
):
    db_software = Software.model_validate(software)
    session.add(db_software)
    await session.commit()
    await session.refresh(db_software)
    return db_software