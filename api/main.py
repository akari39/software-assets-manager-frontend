import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:huiji.233@localhost:5433/dev"
)
print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

# 创建FASTAPI实例
app = FastAPI(lifespan=lifespan)

# CORS跨域中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods= ["*"],
    allow_headers= ["*"],
    allow_origins= ["*"],
)

# 导入并注册路由
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

from routers.dashboard import router as dashboard
app.include_router(dashboard)