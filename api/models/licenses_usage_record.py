from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlmodel import TIMESTAMP, Relationship, SQLModel, Field
from datetime import datetime, timezone

if TYPE_CHECKING:
    from models.softwarelicense import SoftwareLicense
    from models.user  import User

class LicensesUsageRecordBase(SQLModel):
    LicenseID: int = Field(
        foreign_key="software_license.LicenseID", 
        index=True,
        description="关联的LicenseID")

    is_expired: bool = Field(
        default=None,
        description="是否已过期"
    )
    
    UserID: int = Field(
        foreign_key="users.user_id", 
        index=True,
        description="关联的UserID")

    Checkout_time: datetime = Field(
        default=datetime.now(timezone.utc),
        description="领用时间",
        sa_type=TIMESTAMP(timezone=True)
    )

    Duration_Days: int = Field(
        default=0,
        description="领用天数"
    )

    Return_Time: Optional[datetime] = Field(
        default=None,
        description="归还时间",
        sa_type=TIMESTAMP(timezone=True)
    )

    Actually_Return_Time: Optional[datetime] = Field(
        default=None,
        description="实际归还时间",
        sa_type=TIMESTAMP(timezone=True)
    )

class LicensesUsageRecord(LicensesUsageRecordBase, table=True):
    RecordID: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
        description="独立的领用记录ID"
    )
    __tablename__ = "licenses_usage_record"

    software_license: SoftwareLicense = Relationship(
        back_populates="licenses_usage_record",
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )

    user_id: User = Relationship(
        back_populates="licenses_usage_record",
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )

