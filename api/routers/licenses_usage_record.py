from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from models.softwarelicense import SoftwareLicense
from models.user import User
from models.licenses_usage_record import LicensesUsageRecord
from dependencies import get_session
from utils.jwt import get_current_user
from schemas.licenses_usage_record import LicensesUsageRecordRead, LicensesUsageRecordCreate, LicensesUsageRecordRenew

router = APIRouter(prefix="/licenses_usage_records", tags=["Licenses Apply & Return & Renew"])


@router.post("/apply", response_model=LicensesUsageRecordRead, status_code=status.HTTP_201_CREATED)
async def apply_license(
    request: LicensesUsageRecordCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    用户申请一个 license。
    - 检查 license 是否存在
    - 检查 license 是否可用（无活跃 usage record）
    - 检查用户职级是否满足 LvLimit 要求
    - 创建 usage record
    - 修改 license 状态为 已分配
    """

    # 获取当前用户信息
    user_db = current_user

    # 查询对应的 license
    license_db = await session.get(SoftwareLicense, request.LicenseID)
    if not license_db:
        raise HTTPException(status_code=404, detail="License not found")

    # 检查 license 是否已被占用
    active_usage = await session.execute(
        select(LicensesUsageRecord).where(
            LicensesUsageRecord.LicenseID == request.LicenseID,
            LicensesUsageRecord.Actually_Return_Time.is_(None)
        )
    )
    if active_usage.scalars().first():
        raise HTTPException(status_code=409, detail="License is already in use")

    # 检查用户职级是否符合要求
    if license_db.LvLimit is not None and user_db.employee.level < license_db.LvLimit:
        raise HTTPException(
            status_code=403,
            detail=f"User level {user_db.employee.level} does not meet required level {license_db.LvLimit}"
        )

    # 计算归还时间
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

    # 更新 license 状态
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
    """
    用户通过 usage record ID 归还 license。
    - 检查 usage record 是否存在
    - 确保该 record 属于当前用户
    - 确保尚未归还（Actually_Return_Time 为空）
    - 设置 Actually_Return_Time
    - 将 license 状态改为空闲
    """

    record_id = request.RecordID

    # 查询 usage record
    usage_record = await session.get(LicensesUsageRecord, record_id)
    if not usage_record:
        raise HTTPException(status_code=404, detail="Usage record not found")

    # 检查是否属于当前用户
    if usage_record.UserID != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to return this license"
        )

    # 检查是否已经归还
    if usage_record.Actually_Return_Time is not None:
        raise HTTPException(status_code=400, detail="License has already been returned")

    # 设置实际归还时间
    usage_record.Actually_Return_Time = datetime.now(timezone.utc)
    usage_record.is_expired = True


    # 获取对应的 license 并更新状态
    license_db = await session.get(SoftwareLicense, usage_record.LicenseID)
    if license_db:
        license_db.LicenseStatus = 0  # 表示空闲
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
    """
    用户续借一个 license。
    - 检查 usage record 是否存在
    - 确保该 record 属于当前用户
    - 确保尚未归还（Actually_Return_Time 为空）
    - 延长 Return_Time
    """

    record_id = request.RecordID

    # 查询 usage record
    usage_record = await session.get(LicensesUsageRecord, record_id)
    if not usage_record:
        raise HTTPException(status_code=404, detail="Usage record not found")

    # 检查是否属于当前用户
    if usage_record.UserID != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to renew this license"
        )

    # 检查是否已经归还
    if usage_record.Actually_Return_Time is not None:
        raise HTTPException(status_code=400, detail="Cannot renew a returned license")

    # 计算新的归还时间
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