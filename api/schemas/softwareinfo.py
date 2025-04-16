from sqlmodel import SQLModel, Field
from typing import Optional


class SoftwareInfoBase(SQLModel):
    SoftwareInfoName: str = Field(min_length=1)
    SoftwareInfoType: Optional[int] = None
    SoftwareInfoMatchRule: Optional[str] = None
    
# 請求/響應模型
class SoftwareInfoCreate(SoftwareInfoBase):
    pass

class SoftwareInfoRead(SoftwareInfoBase):
    SoftwareInfoID: int

class SoftwareInfoUpdate(SQLModel):
    SoftwareInfoName: Optional[str] = None
    SoftwareInfoType: Optional[int] = None
    SoftwareInfoMatchRule: Optional[str] = None