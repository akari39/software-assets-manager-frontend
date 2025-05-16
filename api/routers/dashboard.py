import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
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
    now = datetime.now()

    used_query = (
        select(LicensesUsageRecord)
        .where(
            LicensesUsageRecord.UserID == current_user.UserID,
            LicensesUsageRecord.Actually_Return_Time.is_(None)
        )
    )