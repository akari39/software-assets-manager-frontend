from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, SQLModel, Field # 使用 SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, AsyncGenerator, List
from datetime import date, datetime # 导入 date 和 datetime

# --------------------------------------------------
# 1. 定義數據模型 (SQLModel) - 反映數據庫表結構
# --------------------------------------------------
class SoftwareLicenseBase(SQLModel):
    # 使用數據庫實際的列名 (基於之前的討論)
    # Field descriptions are added for clarity
    LicenseID: int = Field(description="关联的软件信息ID")
    LicenseType: str = Field(max_length=100, description="授权模式 (例如: 永久, 订阅-用户)")
    授权状态: str = Field(default="可用", max_length=50, description="当前授权状态 (例如: 可用, 已分配)")
    许可证密钥: Optional[str] = Field(default=None, max_length=500, description="许可证密钥或序列号")
    授权到期时间: Optional[datetime] = Field(default=None, description="授权过期时间 (NULL 表示永久)")
    职级限制: Optional[str] = Field(default=None, max_length=50, description="允许使用的最低职级名称")
    备注: Optional[str] = Field(default=None, description="关于此授权的额外说明")
    # 注意: 数据库管理的创建时间和更新时间通常不在Base模型中定义，除非需要手动管理
    # 如果需要在响应中包含它们，在Read模型中添加

class SoftwareLicense(SoftwareLicenseBase, table=True):
    # 指定表名
    __tablename__ = "软件授权信息"
    # 定义主键
    授权信息ID: Optional[int] = Field(default=None, primary_key=True)
    # 如果数据库自动管理时间戳，可以在这里定义，但通常设为 read-only
    创建时间: Optional[datetime] = Field(default=None, description="记录创建时间 (通常由数据库管理)")
    最后更新时间: Optional[datetime] = Field(default=None, description="记录最后更新时间 (通常由数据库管理)")

# --------------------------------------------------
# 2. 請求/響應模型 (Pydantic Schemas based on SQLModel)
# --------------------------------------------------
class SoftwareLicenseCreate(SoftwareLicenseBase):
    # 创建时不需要提供主键和数据库管理的时间戳
    pass # 继承Base即可，如果需要特殊处理可以在此添加

class SoftwareLicenseRead(SoftwareLicenseBase):
    # 响应时包含主键
    授权信息ID: int
    # 响应时也包含时间戳
    创建时间: Optional[datetime] = None
    最后更新时间: Optional[datetime] = None

class SoftwareLicenseUpdate(SQLModel):
    # 更新时所有字段都是可选的
    LicenseID: Optional[int] = None
    LicenseType: Optional[str] = Field(default=None, max_length=100)
    授权状态: Optional[str] = Field(default=None, max_length=50)
    许可证密钥: Optional[str] = Field(default=None, max_length=500)
    授权到期时间: Optional[datetime] = None
    职级限制: Optional[str] = Field(default=None, max_length=50)
    备注: Optional[str] = None
    # 通常不直接通过API更新时间戳

# --------------------------------------------------
# 3. 創建路由實例
# --------------------------------------------------
router = APIRouter(
    prefix="/softwarelicenses",  # 路由前缀
    tags=["Software Licenses"] # API文档标签
)

# --------------------------------------------------
# 4. 依賴注入 (獲取數據庫會話) - 與你的風格保持一致
# --------------------------------------------------
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    # 假設 engine 在 main.py 中定義並導入
    from main import engine # 需要確保可以從main導入engine
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            # 可以选择在这里记录日志
            # logger.error(f"Database session error: {e}")
            raise HTTPException(status_code=500, detail=f"Database error occurred: {e}")
        finally:
            await session.close()


# --------------------------------------------------
# 5. 路由處理函數 (CRUD Operations)
# --------------------------------------------------

@router.post("/", response_model=SoftwareLicenseRead, status_code=status.HTTP_201_CREATED)
async def create_license(
    license_in: SoftwareLicenseCreate, # 使用Create模型接收请求体
    session: AsyncSession = Depends(get_session)
):
    """
    创建一条新的软件授权记录。
    """
    # Optional: 在这里添加业务逻辑验证，例如检查 softwareID 是否存在
    # result = await session.get(SoftwareInfo, license_in.LicenseID) # 假设SoftwareInfo模型存在
    # if not result:
    #     raise HTTPException(status_code=400, detail=f"Software with ID {license_in.LicenseID} not found")

    # 使用 SQLModel 的 model_validate 创建 ORM 实例
    db_license = SoftwareLicense.model_validate(license_in)
    session.add(db_license)
    try:
        await session.commit()
        await session.refresh(db_license) # 刷新以获取数据库生成的主键和时间戳
        return db_license # 返回创建的对象 (使用Read模型进行序列化)
    except SQLAlchemyError as e:
        await session.rollback()
        # 可以记录更详细的错误日志
        raise HTTPException(status_code=500, detail=f"Database commit failed: {e}")

@router.get("/", response_model=List[SoftwareLicenseRead])
async def read_licenses(
    # 添加过滤参数示例
    license_type: Optional[str] = Query(None, description="按LicenseType筛选"),
    status: Optional[str] = Query(None, description="按授权状态筛选"),
    software_id: Optional[int] = Query(None, description="按关联LicenseID筛选"),
    # 分页参数
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_session)
):
    """
    获取软件授权记录列表，支持分页和筛选。
    """
    offset = (page - 1) * limit
    query = select(SoftwareLicense)

    # 应用筛选条件
    if license_type is not None:
        query = query.where(SoftwareLicense.LicenseType == license_type)
    if status is not None:
        query = query.where(SoftwareLicense.授权状态 == status)
    if software_id is not None:
        query = query.where(SoftwareLicense.LicenseID == software_id)

    # 执行查询并应用分页和排序
    result = await session.execute(
        query.offset(offset).limit(limit).order_by(SoftwareLicense.授权信息ID) # 按主键排序
    )
    licenses = result.scalars().all()
    return licenses # Pydantic 会自动使用 SoftwareLicenseRead 进行序列化

@router.get("/{license_id}", response_model=SoftwareLicenseRead)
async def read_license(
    license_id: int, # 路径参数接收ID
    session: AsyncSession = Depends(get_session)
):
    """
    根据ID获取单条软件授权记录。
    """
    # 使用 session.get 高效获取主键对应的记录
    db_license = await session.get(SoftwareLicense, license_id)
    if not db_license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Software license with ID {license_id} not found"
        )
    return db_license

@router.put("/{license_id}", response_model=SoftwareLicenseRead)
async def update_license(
    license_id: int,
    license_in: SoftwareLicenseUpdate, # 使用Update模型接收请求体
    session: AsyncSession = Depends(get_session)
):
    """
    更新指定ID的软件授权记录。
    """
    db_license = await session.get(SoftwareLicense, license_id)
    if not db_license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Software license with ID {license_id} not found"
        )

    # 获取请求中实际提供的字段值 (排除未设置的None值)
    update_data = license_in.model_dump(exclude_unset=True)

    # 动态更新模型实例的属性
    for key, value in update_data.items():
        setattr(db_license, key, value)

    session.add(db_license) # 将更改添加到会话
    try:
        await session.commit()
        await session.refresh(db_license) # 刷新以获取可能由数据库更新的字段（如最后更新时间）
        return db_license
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit failed: {e}")

@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_license(
    license_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    根据ID删除软件授权记录。
    成功删除后返回 204 No Content。
    """
    db_license = await session.get(SoftwareLicense, license_id)
    if not db_license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Software license with ID {license_id} not found"
        )

    await session.delete(db_license)
    try:
        await session.commit()
        # 对于 204 状态码，不需要返回任何内容
        return None # Explicitly return None or use Response(status_code=...)
    except SQLAlchemyError as e:
        await session.rollback()
        # 考虑外键约束等可能导致删除失败的情况
        raise HTTPException(status_code=500, detail=f"Database delete failed: {e}")