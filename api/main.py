# api/main.py

import logging
import sys

# 配置基础日志，以便 logger.error() 的输出能被看到
logging.basicConfig(
    level=logging.DEBUG, # 设置为 DEBUG 以捕获所有级别的日志，方便调试
    stream=sys.stdout,   # 输出到控制台
    format="%(levelname)-8s %(asctime)s [%(name)s:%(lineno)d] %(message)s" # 日志格式
)


import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine #, AsyncSession # AsyncSession 没直接用
# from sqlalchemy.orm import sessionmaker # sessionmaker 也没直接用

# --- 模型导入 ---
# 确保所有模型都在这里或通过 routers 间接导入
from models.employee import Employee
from models.user import User
from models.softwareinfo import SoftwareInfo
from models.softwarelicense import SoftwareLicense
from models.licenses_usage_record import LicensesUsageRecord

# --- Schema 导入 (如果需要在 update_forward_refs 中使用) ---
# from schemas.softwareinfo import SoftwareInfoRead # 示例
# from schemas.SoftwareLicenseList_With_SoftwareInfo import SoftwareLicenseReadWithInfo # 示例

# --- 路由导入 ---
# 稍后 app.include_router
from routers.softwareinfo import router as softwareinfo_router
from routers.softwarelicense import router as softwarelicense_router
from routers.SoftwareLicenseList_With_SoftwareInfo import router as SoftwareLicenseList_With_SoftwareInfo_router
from routers.employee import router as employee_router # 避免与模型名冲突
from routers.user import router as user_router       # 避免与模型名冲突


# --- 更新 SQLModel 的前向引用 ---
# 这个函数必须在所有模型都已定义 (即导入) 之后，
# 并且在 SQLAlchemy 尝试配置它们 (例如通过访问 __mapper__ 或调用 create_all) 之前调用。
def update_all_forward_refs():
    # 确保类已实际加载 (通常 import 就够了)
    # 按需为你的模型调用 update_forward_refs
    if 'User' in globals() and hasattr(User, 'update_forward_refs'): User.model_rebuild()
    if 'Employee' in globals() and hasattr(Employee, 'update_forward_refs'): Employee.model_rebuild()
    if 'SoftwareInfo' in globals() and hasattr(SoftwareInfo, 'update_forward_refs'): SoftwareInfo.model_rebuild()
    if 'SoftwareLicense' in globals() and hasattr(SoftwareLicense, 'update_forward_refs'): SoftwareLicense.model_rebuild()
    if 'LicensesUsageRecord' in globals() and hasattr(LicensesUsageRecord, 'update_forward_refs'): LicensesUsageRecord.model_rebuild()

    # 如果 Schema 也使用了前向引用 (通常是 Schema 引用其他 Schema)
    # 例如:
    # from schemas.softwareinfo import SoftwareInfoRead
    # from schemas.SoftwareLicenseList_With_SoftwareInfo import SoftwareLicenseReadWithInfo
    # if 'SoftwareLicenseReadWithInfo' in globals() and hasattr(SoftwareLicenseReadWithInfo, 'update_forward_refs'):
    #     SoftwareLicenseReadWithInfo.model_rebuild(SoftwareInfoRead=SoftwareInfoRead) # 将实际类型作为参数传递

update_all_forward_refs()  # 在全局作用域调用，确保在访问 __mapper__ 前执行
# ------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:huiji.233@localhost:5433/dev"
)
engine = create_async_engine(DATABASE_URL, echo=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # update_all_forward_refs() # 已在全局调用
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)

# 注册路由
app.include_router(softwareinfo_router)
app.include_router(softwarelicense_router)
app.include_router(SoftwareLicenseList_With_SoftwareInfo_router)
app.include_router(employee_router)
app.include_router(user_router)

