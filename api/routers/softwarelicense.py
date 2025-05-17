from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, AsyncGenerator, List
from datetime import date, datetime, timezone
from dependencies import get_session
from models.softwarelicense import SoftwareLicense
from schemas.softwarelicense import SoftwareLicenseCreate, SoftwareLicenseRead, SoftwareLicenseUpdate
from utils.jwt import get_current_user, get_current_admin

# 创建一个API路由实例，前缀为/softwarelicense，用于处理软件许可证相关请求
router = APIRouter(
    prefix="/softwarelicense",
    tags=["Software License"]
)

# 创建一个新的软件许可证
@router.post("/", response_model=SoftwareLicenseRead, status_code=status.HTTP_201_CREATED)
async def create_license(
    license: SoftwareLicenseCreate,
    session: AsyncSession = Depends(get_session)
):
    db_license = SoftwareLicense.model_validate(license)
    # 设置创建时间和最后更新时间
    db_license.CreateTime = datetime.now(timezone.utc)
    db_license.LastUpdateTime = datetime.now(timezone.utc)
    session.add(db_license)
    try:
        await session.commit()
        await session.refresh(db_license)
        return db_license
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")

# 获取所有软件许可证列表，支持按授权类型、状态和关联软件ID筛选分页查询
@router.get("/", response_model=List[SoftwareLicenseRead])
async def read_licenses(
    license_type: Optional[int] = Query(None, description="按授权类型筛选"),
    status: Optional[int] = Query(None, description="按授权状态筛选"),
    software_id: Optional[int] = Query(None, description="按关联软件ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_session)
):
    offset = (page - 1) * limit
    query = select(SoftwareLicense).options(selectinload(SoftwareLicense.software_info), selectinload(SoftwareLicense.usage_records.user_id))

    if license_type is not None:
        query = query.where(SoftwareLicense.LicenseType == license_type)
    if status is not None:
        query = query.where(SoftwareLicense.LicenseStatus == status)
    if software_id is not None:
        query = query.where(SoftwareLicense.SoftwareInfoID == software_id)

    result = await session.execute(
        query.offset(offset).limit(limit).order_by(SoftwareLicense.LicenseID)
    )
    licenses = result.scalars().all()
    return licenses

# 根据指定的许可证ID获取详细信息
@router.get("/{license_id}", response_model=SoftwareLicenseRead)
async def read_license(
    license_id: int,
    session: AsyncSession = Depends(get_session)
):
    db_license = await session.get(SoftwareLicense, license_id)
    if not db_license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"软件授权ID {license_id} 不存在"
        )
    return db_license

# 更新指定ID的软件许可证信息
@router.put("/{license_id}", response_model=SoftwareLicenseRead)
async def update_license(
    license_id: int,
    license_in: SoftwareLicenseUpdate,
    session: AsyncSession = Depends(get_session)
):
    db_license = await session.get(SoftwareLicense, license_id)
    if not db_license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"软件授权ID {license_id} 不存在"
        )

    update_data = license_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_license, key, value)

    db_license.LastUpdateTime = datetime.now(timezone.utc)

    session.add(db_license)
    try:
        await session.commit()
        await session.refresh(db_license)
        return db_license
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")

# 删除指定ID的软件许可证
@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT,dependencies= Depends(get_current_admin))
async def delete_license(
    license_id: int,
    session: AsyncSession = Depends(get_session)
):
    db_license = await session.get(SoftwareLicense, license_id)
    if not db_license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"软件授权ID {license_id} 不存在"
        )

    await session.delete(db_license)
    try:
        await session.commit()
        return None
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"授权删除失败，可能有关联的数据存在: {e}")