import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models.employee import Employee
from models.user import User
from models.softwareinfo import SoftwareInfo
from models.softwarelicense import SoftwareLicense
from models.licenses_usage_record import LicensesUsageRecord

# 數據庫配置 (僅保留在main.py)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:huiji.233@localhost:5433/dev"
)
engine = create_async_engine(DATABASE_URL, echo=True)

'''
def update_all_forward_refs():
    Employee.update_forward_refs()
    User.update_forward_refs()
    SoftwareInfo.update_forward_refs()
    SoftwareLicense.update_forward_refs()
    LicensesUsageRecord.update_forward_refs()
'''

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

# 創建FastAPI實例
app = FastAPI(lifespan=lifespan)

origins = ["*"]

# 中間件配置
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins= origins,
)

# 導入並註冊路由
from routers.softwareinfo import router as softwareinfo_router
app.include_router(softwareinfo_router)

from routers.softwarelicense import router as softwarelicense_router
app.include_router(softwarelicense_router)

from routers.SoftwareLicenseList_With_SoftwareInfo import router as SoftwareLicenseList_With_SoftwareInfo_router
app.include_router(SoftwareLicenseList_With_SoftwareInfo_router)

from routers.employee import router as employee
app.include_router(employee)

from routers.user import router as user
app.include_router(user)

from routers.auth import router as auth
app.include_router(auth)

from routers.licenses_usage_record import router as licenses_usage_record
app.include_router(licenses_usage_record)

from models.softwarelicense import SoftwareLicense

# 打印 Pydantic 字段（仅基础字段）
print("Pydantic model_fields:")
print(SoftwareLicense.model_fields.keys())

# 打印 SQLAlchemy ORM 字段（含关系字段）
print("\nSQLAlchemy __mapper__.attrs:")
print(list(SoftwareLicense.__mapper__.attrs.keys()))