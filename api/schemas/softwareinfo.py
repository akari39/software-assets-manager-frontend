from sqlmodel import SQLModel, Field
from typing import Optional


class SoftwareInfoBase(SQLModel):
    SoftwareInfoName: str = Field(min_length=1)
    SoftwareInfoType: Optional[int] = Field(default=0, 
    description="软件信息类型," \
    "0=操作系统授权" \
    "1=办公类软件" \
    "2=开发类软件" \
    "3=设计类软件" \
    "4=流媒体访问许可" \
    "5=其他")
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