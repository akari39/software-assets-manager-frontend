from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import TIMESTAMP


if TYPE_CHECKING:
    from models.softwareinfo import SoftwareInfo
    from models.licenses_usage_record import LicensesUsageRecord

class SoftwareLicenseBase(SQLModel):
    SoftwareInfoID: int = Field(
        foreign_key="software_info.SoftwareInfoID", 
        index=True,
        description="关联的SoftwareInfoID")
    LicenseType: int = Field(description="授权模式 (0为月度订阅,1为年度订阅,2为永久)")
    LicenseStatus: int = Field(default="0", description="当前状态(0为可用,1为占用,2为已过期)")
    LicenseKey: Optional[str] = Field(default=None, max_length=500, description="LicenseKey或序列号")
    LicenseExpiredDate: Optional[datetime] = Field(
        default=None, 
        description="授权过期时间 (NULL 表示永久)",
        sa_type=TIMESTAMP(timezone=True)
        )
    LvLimit: Optional[int] = Field(default=None, description="允许使用的最低职级")
    Remark: Optional[str] = Field(default=None, description="备注")
    # 注意: 数据库管理的创建时间和更新时间通常不在Base模型中定义，除非需要手动管理
    # 如果需要在响应中包含它们，在Read模型中添加

class SoftwareLicense(SoftwareLicenseBase, table=True):
    # 指定表名
    __tablename__ = "software_license"
    # 定义主键
    LicenseID: Optional[int] = Field(default=None, primary_key=True)
    # 如果数据库自动管理时间戳，可以在这里定义，但通常设为 read-only
    CreateTime: Optional[datetime] = Field(
        default=None,
        description="记录创建时间 (由数据库自动管理)",
        sa_type=TIMESTAMP(timezone=True)
    )

    LastUpdateTime: Optional[datetime] = Field(
        default=None,
        description="记录最后更新时间 (由应用代码管理)",
        sa_type=TIMESTAMP(timezone=True)
    )

    software_info: SoftwareInfo = Relationship(
        back_populates="software_license",
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
        )
    
    usage_records: list["LicensesUsageRecord"] = Relationship(
        back_populates="software_license",
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )