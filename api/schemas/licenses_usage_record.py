from models.licenses_usage_record import LicensesUsageRecordBase
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LicensesUsageRecordCreate(LicensesUsageRecordBase):
    LicenseID: int
    Duration_Days: int

class LicensesUsageRecordApply(BaseModel):
    LicenseID: int
    Duration_Days: int

class LicensesUsageRecordReturn(BaseModel):
    LicenseID: int

class LicensesUsageRecordRead(LicensesUsageRecordBase):
    RecordID: int

class LicensesUsageRecordUpdate(BaseModel):
    IsActiveRecord: Optional[int] = None
    UserID: Optional[int] = None
    Checkout_time: Optional[datetime] = None
    Duration_Days: Optional[int] = None
    Return_Time: Optional[datetime] = None
    Actually_Return_Time: Optional[datetime] = None

class LicensesUsageRecordRenew(BaseModel):
    RecordID: int
    Renew_Days: int