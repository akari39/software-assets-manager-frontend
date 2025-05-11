from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select # 使用 SQLModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, AsyncGenerator, List
from datetime import date, datetime, timezone # 导入 date 和 datetime
from dependencies import get_session
from models.softwarelicense import SoftwareLicense
from schemas.softwarelicense import SoftwareLicenseCreate, SoftwareLicenseRead, SoftwareLicenseUpdate

router = APIRouter(
    prefix="/softwarelicense",  # 路由前缀
    tags=["Software License"] # API文档标签
)

@router.post("/", response_model=SoftwareLicenseRead, status_code=status.HTTP_201_CREATED)
async def create_license(
    license: SoftwareLicenseCreate, # 使用Create模型接收请求体
    session: AsyncSession = Depends(get_session)
):
    # 使用 SQLModel 的 model_validate 创建 ORM 实例
    db_license = SoftwareLicense.model_validate(license)
    db_license.CreateTime = datetime.now(timezone.utc) # 设置初始更新时间
    db_license.LastUpdateTime = datetime.now(timezone.utc) # 设置初始更新时间
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
    license_type: Optional[int] = Query(None, description="按LicenseType筛选"),
    status: Optional[int] = Query(None, description="按LicenseStatus筛选"),
    software_id: Optional[int] = Query(None, description="按关联SoftwareInfoID筛选"),
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
        query = query.where(SoftwareLicense.LicenseStatus == status)
    if software_id is not None:
        query = query.where(SoftwareLicense.SoftwareInfoID == software_id)

    # 执行查询并应用分页和排序
    result = await session.execute(
        query.offset(offset).limit(limit).order_by(SoftwareLicense.LicenseID) # 按主键排序
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

    db_license.LastUpdateTime = datetime.now(timezone.utc) # 更新时间戳

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