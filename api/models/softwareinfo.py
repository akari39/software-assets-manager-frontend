from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING, Optional
from schemas.softwareinfo import SoftwareInfoBase

if TYPE_CHECKING:
    from models.softwarelicense import SoftwareLicense

class SoftwareInfo(SoftwareInfoBase, table=True):
    __tablename__ = "software_info" 
    SoftwareInfoID: Optional[int] = Field(default=None, primary_key=True)

    licenses: list["SoftwareLicense"] = Relationship(
        back_populates="software_info",
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )