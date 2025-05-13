from __future__ import annotations
from typing import Optional
from schemas.softwarelicense import SoftwareLicenseRead
from schemas.softwareinfo import SoftwareInfoRead

class SoftwareLicenseReadWithInfo(SoftwareLicenseRead):
    software_info: Optional[SoftwareInfoRead] = None