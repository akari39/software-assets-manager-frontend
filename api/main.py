import asyncio
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.employee import Employee
from utils.PwdHash import get_password_hash

DEFAULT_ADMIN = {
    "employee_id": "admin",
    "password": "adminpassword",
    "name": "Administrator",
    "department": "IT",
    "level": 5,
    "status": 0
}
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:huiji.233@localhost:5433/dev"
)
print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)


print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("Sleeping for 5 seconds...")
time.sleep(10)
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("Sleep complete.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        async with session.begin():
            # 检查是否存在 admin 用户
            result = await session.execute(
                select(User).join(Employee).where(Employee.employee_id == DEFAULT_ADMIN["employee_id"])
            )
            existing_admin = result.scalars().first()

            if not existing_admin:
                # 创建员工（如果不存在）
                admin_employee = await session.get(Employee, DEFAULT_ADMIN["employee_id"])
                if not admin_employee:
                    admin_employee = Employee(
                        employee_id=DEFAULT_ADMIN["employee_id"],
                        name=DEFAULT_ADMIN["name"],
                        department=DEFAULT_ADMIN["department"],
                        level=DEFAULT_ADMIN["level"],
                        status=DEFAULT_ADMIN["status"]
                    )
                    session.add(admin_employee)

                # 创建用户
                hashed_password = get_password_hash(DEFAULT_ADMIN["password"])
                admin_user = User(
                    employee_id=DEFAULT_ADMIN["employee_id"],
                    hashed_password=hashed_password,
                    permissions=1,  # 管理员权限
                    status=0
                )
                session.add(admin_user)
                await session.commit()
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("✅ Default admin account created.")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                # 更新 test1 到 test5 的密码
                for i in range(1, 6):
                    test_id = f"test{i}"
                    test_password = f"test{i}"

                    # 查询 test 用户
                    result = await session.execute(
                        select(User).join(Employee).where(Employee.employee_id == test_id)
                    )
                    user = result.scalars().first()

                    if user:
                        # 更新密码
                        user.hashed_password = get_password_hash(test_password)
                        session.add(user)
                        ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(f"✅ Password for {test_id} has been updated.")
                        ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    else:
                        ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(f"⚠️ {test_id} does not exist. Skipping password update.")
                        ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            else:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("ℹ️ Admin account already exists.")
                print("Skipped test account password update.")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

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
