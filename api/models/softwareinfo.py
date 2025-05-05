from sqlmodel import SQLModel, Field
from typing import Optional
from schemas.softwareinfo import SoftwareInfoBase

class SoftwareInfo(SoftwareInfoBase, table=True):
    __tablename__ = "software_info" 
    SoftwareInfoID: Optional[int] = Field(default=None, primary_key=True)