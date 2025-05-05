# /Users/huiji/Dev/software-assets-manager/api/routers/SoftwareLicense_ManualJoin.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
# 注意：這次我們不直接使用 selectinload
from typing import Optional, List, Dict

# --- 導入依賴、模型和 Schema ---
from ..dependencies import get_session
from ..models.softwarelicense import SoftwareLicense
from ..models.softwareinfo import SoftwareInfo
# 導入基礎讀取 Schema 和新的組合 Schema
from ..schemas.softwarelicense import SoftwareLicenseRead
from ..schemas.softwareinfo import SoftwareInfoRead
from ..schemas.SoftwareLicenseList_With_SoftwareInfo import SoftwareLicenseReadWithInfo
# --------------------------------

# 創建新的路由實例
router = APIRouter(
    prefix="/licenses_with_info", # 使用不同的前綴
    tags=["Licenses With Info"] # API 文檔標籤
)

# --- API 端點：獲取列表 (手動組合) ---
@router.get("/", response_model=List[SoftwareLicenseReadWithInfo])
async def get_licenses_list_manual_join(
    # --- 篩選和分頁參數 ---
    license_type: Optional[int] = Query(None, description="按授权模式筛选"),
    status_filter: Optional[int] = Query(None, alias="status", description="按当前状态筛选"),
    software_id: Optional[int] = Query(None, description="按关联软件ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    # ----------------------
    session: AsyncSession = Depends(get_session)
):
    """
    獲取軟件授權列表，然後根據 ID 手動查詢關聯的軟件信息並組合返回。
    """
    offset = (page - 1) * limit

    # 1. 查詢 SoftwareLicense 列表
    license_statement = select(SoftwareLicense)
    # 應用篩選
    if license_type is not None:
        license_statement = license_statement.where(SoftwareLicense.LicenseType == license_type)
    if status_filter is not None:
        license_statement = license_statement.where(SoftwareLicense.LicenseStatus == status_filter)
    if software_id is not None:
        license_statement = license_statement.where(SoftwareLicense.SoftwareInfoID == software_id)
    # 應用分頁
    license_statement = license_statement.offset(offset).limit(limit)

    result_licenses = await session.execute(license_statement)
    licenses_db: List[SoftwareLicense] = result_licenses.scalars().all()

    if not licenses_db:
        return [] # 如果沒有授權記錄，直接返回空列表

    # 2. 提取所有需要的 SoftwareInfoID
    software_info_ids = {lic.SoftwareInfoID for lic in licenses_db if lic.SoftwareInfoID is not None}

    software_info_map: Dict[int, SoftwareInfoRead] = {}
    if software_info_ids: # 僅在有 ID 需要查詢時執行
        # 3. 查詢對應的 SoftwareInfo (使用 IN 查詢優化)
        info_statement = select(SoftwareInfo).where(SoftwareInfo.SoftwareInfoID.in_(software_info_ids))
        result_info = await session.execute(info_statement)
        software_infos_db: List[SoftwareInfo] = result_info.scalars().all()
        # 4. 將 SoftwareInfo 轉換為 Read Schema 並映射到字典
        for info_db in software_infos_db:
            software_info_map[info_db.SoftwareInfoID] = SoftwareInfoRead.model_validate(info_db)

    # 5. 組合數據
    combined_results: List[SoftwareLicenseReadWithInfo] = []
    for license_db in licenses_db:
        # 將授權數據轉換為 Read Schema
        license_read = SoftwareLicenseRead.model_validate(license_db)
        # 從 map 中查找對應的 info 數據
        info_read = software_info_map.get(license_db.SoftwareInfoID)
        # 創建組合後的 Schema 實例
        combined = SoftwareLicenseReadWithInfo(
            **license_read.model_dump(), # 展開 license 數據
            software_info=info_read      # 添加 info 數據
        )
        combined_results.append(combined)

    # 6. 返回組合後的列表
    return combined_results

@router.get("/search", response_model=List[SoftwareLicenseReadWithInfo]) #
async def search_licenses_with_info(
    # --- 搜索參數 ---
    search_category: str = Query( # 使 category 成为必需参数
        ..., # 使用 ... 表示必需
        description="Search category (e.g., software_name, software_type, license_type, license_status)"
    ),
    search_value: str = Query( # 使 value 成为必需参数
        ..., # 使用 ... 表示必需
        description="Search value (case-insensitive for name)"
    ),
     # --- 可选的基本篩選和分頁參數 ---
    license_type: Optional[int] = Query(None, description="按授权模式筛选 (可与搜索结合)"),
    status_filter: Optional[int] = Query(None, alias="status", description="按当前状态筛选 (可与搜索结合)"),
    software_id: Optional[int] = Query(None, description="按关联软件ID筛选 (可与搜索结合)"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    # ----------------------
    session: AsyncSession = Depends(get_session) #
):
    """
    根据指定类别和值搜索软件授权列表，并组合关联的软件信息返回。
    支持结合基本筛选条件和分页。
    """
    offset = (page - 1) * limit

    # --- 构建基础查询 ---
    query = select(SoftwareLicense, SoftwareInfo).outerjoin(
        SoftwareInfo, SoftwareLicense.SoftwareInfoID == SoftwareInfo.SoftwareInfoID #
    )

    # --- 应用搜索条件 (必需) ---
    try:
        if search_category == "software_name":
            query = query.where(SoftwareInfo.SoftwareInfoName.ilike(f"%{search_value}%")) #
        elif search_category == "software_type":
            query = query.where(SoftwareInfo.SoftwareInfoType == int(search_value)) #
        elif search_category == "license_type":
            query = query.where(SoftwareLicense.LicenseType == int(search_value)) #
        elif search_category == "license_status":
            query = query.where(SoftwareLicense.LicenseStatus == int(search_value)) #
        else:
            raise HTTPException(status_code=400, detail=f"Invalid search category: {search_category}")
    except ValueError:
         raise HTTPException(status_code=400, detail=f"Invalid search value '{search_value}' for category '{search_category}'. Expected an integer.")
    except AttributeError:
         # 如果 SoftwareInfo 为 None 但尝试按其字段搜索，SQLAlchemy 通常会处理，但以防万一
         raise HTTPException(status_code=400, detail=f"Cannot search by '{search_category}' if related software info is missing.")

    # --- 应用可选的筛选条件 ---
    if license_type is not None:
        query = query.where(SoftwareLicense.LicenseType == license_type) #
    if status_filter is not None:
        query = query.where(SoftwareLicense.LicenseStatus == status_filter) #
    if software_id is not None:
        query = query.where(SoftwareLicense.SoftwareInfoID == software_id) #

    # --- 应用分页和排序 ---
    query = query.order_by(SoftwareLicense.LicenseID).offset(offset).limit(limit) #

    # --- 执行查询 ---
    result = await session.execute(query)
    results_db: List[Tuple[SoftwareLicense, Optional[SoftwareInfo]]] = result.all()

    # --- 组合数据 ---
    combined_results: List[SoftwareLicenseReadWithInfo] = []
    for license_db, info_db in results_db:
        license_read = SoftwareLicenseRead.model_validate(license_db) #
        info_read = SoftwareInfoRead.model_validate(info_db) if info_db else None #

        combined = SoftwareLicenseReadWithInfo( #
            **license_read.model_dump(),
            software_info=info_read
        )
        combined_results.append(combined)

    # --- 返回組合後的列表 ---
    return combined_results


# --- API 端點：根據 ID 獲取單條記錄 (手動組合) ---
@router.get("/{license_id}", response_model=SoftwareLicenseReadWithInfo)
async def get_single_license_manual_join(
    license_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    根據 LicenseID 獲取單個軟件授權，然後手動查詢關聯軟件信息並組合返回。
    """
    # 1. 查詢 SoftwareLicense
    license_db = await session.get(SoftwareLicense, license_id)
    if not license_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Software license with ID {license_id} not found"
        )

    # 2. 查詢對應的 SoftwareInfo
    info_read: Optional[SoftwareInfoRead] = None
    if license_db.SoftwareInfoID is not None:
        info_db = await session.get(SoftwareInfo, license_db.SoftwareInfoID)
        if info_db:
            info_read = SoftwareInfoRead.model_validate(info_db) # 轉換為 Read Schema

    # 3. 組合數據
    license_read = SoftwareLicenseRead.model_validate(license_db)
    combined_result = SoftwareLicenseReadWithInfo(
        **license_read.model_dump(),
        software_info=info_read
    )

    # 4. 返回組合結果
    return combined_result