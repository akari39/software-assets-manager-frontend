from typing import Optional
from sqlmodel import SQLModel

class Dashboard(SQLModel):
    used_licenses: int
    approching_expired_licenses: int
    apllicable_licenses: int