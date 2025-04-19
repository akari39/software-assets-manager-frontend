from __future__ import annotations
from sqlmodel import select, SQLModel, Field, Relationship # 使用 SQLModel
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone # 导入 date 和 datetime
from sqlalchemy import TIMESTAMP


if TYPE_CHECKING:
    from .softwareinfo import SoftwareInfo
# --------------------------------------------------
# 1. 定義數據模型 (SQLModel) - 反映數據庫表結構
# --------------------------------------------------
class SoftwareLicenseBase(SQLModel):
    # 使用數據庫實際的列名 (基於之前的討論)
    # Field descriptions are added for clarity
    SoftwareInfoID: int = Field(
        foreign_key="software_info.SoftwareInfoID", 
        description="关联的软件信息ID")
    LicenseType: int = Field(description="授权模式 (例如: 永久, 订阅-用户)")
    LicenseStatus: int = Field(default="0", description="当前状态 (例如: 可用, 已分配)")
    LicenseKey: Optional[str] = Field(default=None, max_length=500, description="LicenseKey或序列号")
    LicenseExpiredDate: Optional[datetime] = Field(
        default=None, 
        description="授权过期时间 (NULL 表示永久)",
        sa_type=TIMESTAMP(timezone=True)
        )
    LvLimit: Optional[int] = Field(default=None, description="允许使用的最低职级名称")
    Remark: Optional[str] = Field(default=None, description="关于此授权的额外说明")
    # 注意: 数据库管理的创建时间和更新时间通常不在Base模型中定义，除非需要手动管理
    # 如果需要在响应中包含它们，在Read模型中添加

class SoftwareLicense(SoftwareLicenseBase, table=True):
    # 指定表名
    __tablename__ = "License"
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