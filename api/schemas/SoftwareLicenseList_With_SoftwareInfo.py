from __future__ import annotations
from typing import Optional
from schemas.softwarelicense import SoftwareLicenseRead
from schemas.softwareinfo import SoftwareInfoRead
from schemas.licenses_usage_record import LicensesUsageRecordRead

class SoftwareLicenseReadWithInfo(SoftwareLicenseRead):
    software_info: Optional[SoftwareInfoRead] = None
    latest_usage_record: Optional[LicensesUsageRecordRead] = None