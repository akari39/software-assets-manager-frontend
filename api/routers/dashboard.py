import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models.softwarelicense import SoftwareLicense
from dependencies import get_session
from schemas.dashboard  import Dashboard
from utils.jwt import get_current_user, get_current_admin
from models.user import User
from models.licenses_usage_record  import LicensesUsageRecord

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/", response_model=Dashboard)
async def create_employee(
    current_user: User = Depends(get_current_user),
    Session: AsyncSession = Depends(get_session)
):
    now = datetime.datetime.now()
    used_query = (
        select(LicensesUsageRecord)
        .where(
            LicensesUsageRecord.UserID == current_user.user_id,
            LicensesUsageRecord.Actually_Return_Time.is_(None)
        )
    )
    used_result = await Session.execute(used_query)
    used_count = len(used_result.scalars().all())

    approach_expire_query = (
        select(LicensesUsageRecord)
        .where(
            LicensesUsageRecord.UserID == current_user.user_id,
            LicensesUsageRecord.Actually_Return_Time.is_(None),
            LicensesUsageRecord.Return_Time >= now + datetime.timedelta(days=7)
        )
    )
    approach_expire_result = await Session.execute(approach_expire_query)
    approach_expire_count = len(approach_expire_result.scalars().all())

    available_query = (
        select(SoftwareLicense)
        .where(
            SoftwareLicense.LicenseStatus == 0,
            or_(
                SoftwareLicense.LvLimit.is_(None),
                SoftwareLicense.LvLimit <=  current_user.employee.level
                ),
        )
        )
    available_result = await Session.execute(available_query)
    available_count = len(available_result.scalars().all())

    return Dashboard(
        used_licenses=used_count,
        approching_expired_licenses=approach_expire_count,
        apllicable_licenses=available_count
    )
