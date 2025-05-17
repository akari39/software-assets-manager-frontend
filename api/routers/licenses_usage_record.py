from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

# 导入模型和依赖项
from models.employee import Employee
from models.softwarelicense import SoftwareLicense
from models.user import User
from models.licenses_usage_record import LicensesUsageRecord
from dependencies import get_session
from utils.jwt import get_current_user
from schemas.licenses_usage_record import LicensesUsageRecordRead, LicensesUsageRecordRenew, LicensesUsageRecordApply, LicensesUsageRecordReturn

# 创建路由实例，设置前缀和标签
router = APIRouter(prefix="/licenses_usage_records", tags=["Licenses Apply & Return & Renew"])


@router.post("/apply", response_model=LicensesUsageRecordRead, status_code=status.HTTP_201_CREATED)
async def apply_license(
    request: LicensesUsageRecordApply,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # 获取当前用户信息
    user_db = current_user

    # 查询请求中的许可证是否存在
    license_db = await session.get(SoftwareLicense, request.LicenseID)
    if not license_db:
        raise HTTPException(status_code=404, detail="您请求的授权ID不存在")

    # 检查该许可证是否已经被占用
    active_usage = await session.execute(
        select(LicensesUsageRecord).where(
            LicensesUsageRecord.LicenseID == request.LicenseID,
            LicensesUsageRecord.Actually_Return_Time.is_(None)
        )
    )
    if active_usage.scalars().first():
        raise HTTPException(status_code=409, detail="此授权已被使用")

    # 查询员工信息
    result = await session.execute(
        select(Employee).where(Employee.employee_id == current_user.employee_id)
    )
    employee = result.scalars().first()

    if not employee:
        raise HTTPException(status_code=404, detail="不存在此员工")

    if license_db.LvLimit is not None and employee.level < license_db.LvLimit:
        raise HTTPException(
            status_code=403,
            detail=f"您的职级 {employee.level} 不满足领用需求"
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
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")



@router.post("/return", response_model=LicensesUsageRecordRead, status_code=status.HTTP_200_OK)
async def return_license_by_usage_id(
    request: LicensesUsageRecordReturn,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    license_id = request.LicenseID

    # 查询使用记录
    record_statement = (
        select(LicensesUsageRecord)
        .where(
            LicensesUsageRecord.LicenseID == license_id,
            LicensesUsageRecord.Actually_Return_Time.is_(None)
        )
        .order_by(LicensesUsageRecord.Checkout_time.desc())
        .limit(1)
    )
    if not record_statement:
        raise HTTPException(status_code=404, detail="没有找到使用记录")

    # 确保当前用户有权限归还该许可证
    if record_statement.UserID != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="不能归还非本人的授权"
        )

    # 确认该许可证尚未被归还
    if record_statement.Actually_Return_Time is not None:
        raise HTTPException(status_code=400, detail="无法归还已经归还的授权")

    # 更新实际归还时间和过期状态
    record_statement.Actually_Return_Time = datetime.now(timezone.utc)
    record_statement.is_expired = True

    # 更新许可证状态和最后更新时间
    license_db = await session.get(SoftwareLicense, record_statement.LicenseID)
    if license_db:
        license_db.LicenseStatus = 0
        license_db.LastUpdateTime = datetime.now(timezone.utc)
        session.add(license_db)

    session.add(record_statement)

    try:
        await session.commit()
        await session.refresh(record_statement)
        return record_statement
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")


@router.post("/renew", response_model=LicensesUsageRecordRead, status_code=status.HTTP_200_OK)
async def renew_license(
    request: LicensesUsageRecordRenew,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    license_id = request.RecordID


    record_statement = (
        select(LicensesUsageRecord)
        .where(
            LicensesUsageRecord.LicenseID == license_id,
            LicensesUsageRecord.Actually_Return_Time.is_(None)
        )
        .order_by(LicensesUsageRecord.Checkout_time.desc())
        .limit(1)
    )

    result_records = await session.execute(record_statement)
    usage_record = result_records.scalars().first()
    if  not usage_record:
        raise HTTPException(status_code=404, detail=f"授权ID：{license_id}没被领用")

    # 确保当前用户有权限续借该许可证
    if usage_record.UserID != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="不能更新非本人的授权"
        )

    # 确认该许可证尚未被归还
    if usage_record.Actually_Return_Time is not None:
        raise HTTPException(status_code=400, detail="无法续期已经归还的授权")

    # 更新归还时间
    new_return_time = usage_record.Return_Time + timedelta(days=request.Renew_Days)
    usage_record.Return_Time = new_return_time

    session.add(usage_record)

    try:
        await session.commit()
        await session.refresh(usage_record)
        return usage_record
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")