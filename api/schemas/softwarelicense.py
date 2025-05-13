from sqlmodel import select, SQLModel, Field 
from typing import Optional
from datetime import datetime
from models.softwarelicense import SoftwareLicenseBase

class SoftwareLicenseCreate(SoftwareLicenseBase):
    pass

class SoftwareLicenseRead(SoftwareLicenseBase):
    LicenseID: int
    CreateTime: Optional[datetime] = None
    LastUpdateTime: Optional[datetime] = None

class SoftwareLicenseUpdate(SQLModel):
    SoftwareInfoID: Optional[int] = None
    LicenseType: Optional[int] = Field(default=None)
    LicenseStatus: Optional[int] = Field(default=None)
    LicenseKey: Optional[str] = Field(default=None, max_length=500)
    LicenseExpiredDate: Optional[datetime] = None
    LvLimit: Optional[int] = Field(default=None)
    Remark: Optional[str] = None