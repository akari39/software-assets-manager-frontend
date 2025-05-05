# /Users/huiji/Dev/software-assets-manager/api/schemas/SoftwareLicenseWithInfo.py
from __future__ import annotations
from typing import Optional

# 導入基礎讀取模型
from schemas.softwarelicense import SoftwareLicenseRead
from schemas.softwareinfo import SoftwareInfoRead

# 定義組合 Schema
class SoftwareLicenseReadWithInfo(SoftwareLicenseRead):
    """
    用於 API 響應的組合模型，包含 SoftwareLicense 的基礎信息
    以及手動查詢並附加的 SoftwareInfo 信息。
    """
    software_info: Optional[SoftwareInfoRead] = None # 用於存放查詢到的 SoftwareInfo 數據