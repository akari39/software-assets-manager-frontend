from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

# 导入模型和依赖项
from models.softwarelicense import SoftwareLicense
from models.user import User
from models.licenses_usage_record import LicensesUsageRecord
from dependencies import get_session
from utils.jwt import get_current_user
from schemas.licenses_usage_record import LicensesUsageRecordRead, LicensesUsageRecordCreate, LicensesUsageRecordRenew

# 创建路由实例，设置前缀和标签
router = APIRouter(prefix="/licenses_usage_records", tags=["Licenses Apply & Return & Renew"])


@router.post("/apply", response_model=LicensesUsageRecordRead, status_code=status.HTTP_201_CREATED)
async def apply_license(
    request: LicensesUsageRecordCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # 获取当前用户信息
    user_db = current_user

    # 查询请求中的许可证是否存在
    license_db = await session.get(SoftwareLicense, request.LicenseID)
    if not license_db:
        raise HTTPException(status_code=404, detail="License not found")

    # 检查该许可证是否已经被占用
    active_usage = await session.execute(
        select(LicensesUsageRecord).where(
            LicensesUsageRecord.LicenseID == request.LicenseID,
            LicensesUsageRecord.Actually_Return_Time.is_(None)
        )
    )
    if active_usage.scalars().first():
        raise HTTPException(status_code=409, detail="License is already in use")

    # 检查用户级别是否满足许可证的要求
    if license_db.LvLimit is not None and user_db.employee.level < license_db.LvLimit:
        raise HTTPException(
            status_code=403,
            detail=f"User level {user_db.employee.level} does not meet required level {license_db.LvLimit}"
        )

    # 设置借出时间和归还时间
    checkout_time = datetime.now(timezone.utc)
    return_time = checkout_time + timedelta(days=request.Duration_Days)

    # 创建新的使用记录
    new_record = LicensesUsageRecord(
        LicenseID=request.LicenseID,
        UserID=user_db.user_id,
        Checkout_time=checkout_time,
        Duration_Days=request.Duration_Days,
        Return_Time=return_time,
        is_expired=False,
        Actually_Return_Time=None
    )
    session.add(new_record)

    # 更新许可证状态和最后更新时间
    license_db.LicenseStatus = 1
    license_db.LastUpdateTime = datetime.now(timezone.utc)
    session.add(license_db)

    try:
        await session.commit()
        await session.refresh(new_record)
        return new_record
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")


@router.post("/return", response_model=LicensesUsageRecordRead, status_code=status.HTTP_200_OK)
async def return_license_by_usage_id(
    request: LicensesUsageRecordRead,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    record_id = request.RecordID

    # 查询使用记录
    usage_record = await session.get(LicensesUsageRecord, record_id)
    if not usage_record:
        raise HTTPException(status_code=404, detail="Usage record not found")

    # 确保当前用户有权限归还该许可证
    if usage_record.UserID != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to return this license"
        )

    # 确认该许可证尚未被归还
    if usage_record.Actually_Return_Time is not None:
        raise HTTPException(status_code=400, detail="License has already been returned")

    # 更新实际归还时间和过期状态
    usage_record.Actually_Return_Time = datetime.now(timezone.utc)
    usage_record.is_expired = True

    # 更新许可证状态和最后更新时间
    license_db = await session.get(SoftwareLicense, usage_record.LicenseID)
    if license_db:
        license_db.LicenseStatus = 0
        license_db.LastUpdateTime = datetime.now(timezone.utc)
        session.add(license_db)

    session.add(usage_record)

    try:
        await session.commit()
        await session.refresh(usage_record)
        return usage_record
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")


@router.post("/renew", response_model=LicensesUsageRecordRead, status_code=status.HTTP_200_OK)
async def renew_license(
    request: LicensesUsageRecordRenew,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    record_id = request.RecordID

    # 查询使用记录
    usage_record = await session.get(LicensesUsageRecord, record_id)
    if not usage_record:
        raise HTTPException(status_code=404, detail="Usage record not found")

    # 确保当前用户有权限续借该许可证
    if usage_record.UserID != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to renew this license"
        )

    # 确认该许可证尚未被归还
    if usage_record.Actually_Return_Time is not None:
        raise HTTPException(status_code=400, detail="Cannot renew a returned license")

    # 更新归还时间
    new_return_time = usage_record.Return_Time + timedelta(days=request.RenewDays)
    usage_record.Return_Time = new_return_time

    session.add(usage_record)

    try:
        await session.commit()
        await session.refresh(usage_record)
        return usage_record
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")