from sqlmodel import select, SQLModel, Field # 使用 SQLModel
from typing import Optional
from datetime import date, datetime, timezone # 导入 date 和 datetime
from ..models.softwarelicense import SoftwareLicenseBase

# --------------------------------------------------
# 2. 請求/響應模型 (Pydantic Schemas based on SQLModel)
# --------------------------------------------------
class SoftwareLicenseCreate(SoftwareLicenseBase):
    # 创建时不需要提供主键和数据库管理的时间戳
    pass # 继承Base即可，如果需要特殊处理可以在此添加

class SoftwareLicenseRead(SoftwareLicenseBase):
    # 响应时包含主键
    LicenseID: int
    # 响应时也包含时间戳
    CreateTime: Optional[datetime] = None
    LastUpdateTime: Optional[datetime] = None

class SoftwareLicenseUpdate(SQLModel):
    # 更新时所有字段都是可选的
    SoftwareInfoID: Optional[int] = None
    LicenseType: Optional[int] = Field(default=None)
    LicenseStatus: Optional[int] = Field(default=None)
    LicenseKey: Optional[str] = Field(default=None, max_length=500)
    LicenseExpiredDate: Optional[datetime] = None
    LvLimit: Optional[int] = Field(default=None)
    Remark: Optional[str] = None
    # 通常不直接通过API更新时间戳