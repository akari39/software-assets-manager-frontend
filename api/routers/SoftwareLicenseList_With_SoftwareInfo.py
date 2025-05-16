# 导入必要的模块和依赖
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Tuple
from schemas.licenses_usage_record import LicensesUsageRecordRead
from models.licenses_usage_record import LicensesUsageRecord
from dependencies import get_session  # 获取数据库会话的依赖
from models.softwarelicense import SoftwareLicense  # 软件授权模型
from models.softwareinfo import SoftwareInfo  # 软件信息模型
from schemas.softwarelicense import SoftwareLicenseRead  # 软件授权读取模式
from schemas.softwareinfo import SoftwareInfoRead  # 软件信息读取模式
from schemas.SoftwareLicenseList_With_SoftwareInfo import SoftwareLicenseReadWithInfo  # 包含软件信息的授权读取模式

# 创建API路由实例，前缀为/licenses_with_info，标签为"Licenses With Info"
router = APIRouter(
    prefix="/licenses_with_info",
    tags=["Licenses With Info"]
)

# 获取所有授权列表接口，返回包含软件信息的授权数据
@router.get("/", response_model=List[SoftwareLicenseReadWithInfo])
async def get_licenses_list_manual_join(
    license_type: Optional[int] = Query(None, description="按授权模式筛选"),
    status_filter: Optional[int] = Query(None, alias="status", description="按当前状态筛选"),
    software_id: Optional[int] = Query(None, description="按关联软件ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_session)
):

    offset = (page - 1) * limit
    license_statement = select(SoftwareLicense)

    if license_type is not None:
        license_statement = license_statement.where(SoftwareLicense.LicenseType == license_type)
    if status_filter is not None:
        license_statement = license_statement.where(SoftwareLicense.LicenseStatus == status_filter)
    if software_id is not None:
        license_statement = license_statement.where(SoftwareLicense.SoftwareInfoID == software_id)

    license_statement = license_statement.offset(offset).limit(limit)
    result_licenses = await session.execute(license_statement)
    licenses_db: List[SoftwareLicense] = result_licenses.scalars().all()

    if not licenses_db:
        return []

    # 获取 software info
    software_info_ids = {lic.SoftwareInfoID for lic in licenses_db if lic.SoftwareInfoID is not None}
    software_info_map = {}
    if software_info_ids:
        info_statement = select(SoftwareInfo).where(SoftwareInfo.SoftwareInfoID.in_(software_info_ids))
        result_info = await session.execute(info_statement)
        software_infos_db = result_info.scalars().all()
        for info_db in software_infos_db:
            software_info_map[info_db.SoftwareInfoID] = SoftwareInfoRead.model_validate(info_db)

    # 获取每个 license 的最新 usage record
    license_ids = [lic.LicenseID for lic in licenses_db]
    usage_records_map = {}

    if license_ids:
        record_statement = (
            select(LicensesUsageRecord)
            .where(
                LicensesUsageRecord.LicenseID.in_(license_ids),
                LicensesUsageRecord.Actually_Return_Time.is_(None)
            )
            .order_by(LicensesUsageRecord.Checkout_time.desc())
        )

        result_records = await session.execute(record_statement)
        records_db = result_records.scalars().all()

        # 构建映射：license_id -> 最新 record
        from collections import defaultdict
        grouped_records = defaultdict(list)
        for r in records_db:
            grouped_records(r.LicenseID).append(r)

        # 取每个 license 的第一条（最新）
        for lid in license_ids:
            if grouped_records[lid]:
                usage_records_map[lid] = LicensesUsageRecordRead.model_validate(grouped_records[lid][0])

    # 组合数据
    combined_results = []
    for license_db in licenses_db:
        lic_data = SoftwareLicenseRead.model_validate(license_db)
        info_data = software_info_map.get(license_db.SoftwareInfoID)
        record_data = usage_records_map.get(license_db.LicenseID)

        combined = SoftwareLicenseReadWithInfo(
            **lic_data.model_dump(),
            software_info=info_data,
            latest_usage_record=record_data
        )
        combined_results.append(combined)

    return combined_results


# 搜索授权信息接口
@router.get("/search", response_model=List[SoftwareLicenseReadWithInfo])
async def search_licenses_with_info(
    search_category: str = Query(..., description="搜索类别（例如：software_name, software_type, license_type, license_status）"),
    search_value: str = Query(..., description="搜索值（对名称不区分大小写）"),
    license_type: Optional[int] = Query(None, description="按授权模式筛选 (可与搜索结合)"),
    status_filter: Optional[int] = Query(None, alias="status", description="按当前状态筛选 (可与搜索结合)"),
    software_id: Optional[int] = Query(None, description="按关联软件ID筛选 (可与搜索结合)"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_session)
):

    offset = (page - 1) * limit  # 计算偏移量

    # 查询授权信息并外连接软件信息表
    query = select(SoftwareLicense, SoftwareInfo).outerjoin(
        SoftwareInfo, SoftwareLicense.SoftwareInfoID == SoftwareInfo.SoftwareInfoID
    )

    try:
        # 根据搜索类别添加不同的过滤条件
        if search_category == "software_name":
            query = query.where(SoftwareInfo.SoftwareInfoName.ilike(f"%{search_value}%"))
        elif search_category == "software_type":
            query = query.where(SoftwareInfo.SoftwareInfoType == int(search_value))
        elif search_category == "license_type":
            query = query.where(SoftwareLicense.LicenseType == int(search_value))
        elif search_category == "license_status":
            query = query.where(SoftwareLicense.LicenseStatus == int(search_value))
        else:
            raise HTTPException(status_code=400, detail=f"无效的搜索类别: {search_category}")
    except ValueError:
         raise HTTPException(status_code=400, detail=f"无效的搜索值 '{search_value}' 对于类别 '{search_category}'. 需要整数。")
    except AttributeError:
         raise HTTPException(status_code=400, detail=f"如果缺少相关软件信息，则无法按 '{search_category}' 进行搜索。")

    # 添加额外的过滤条件
    if license_type is not None:
        query = query.where(SoftwareLicense.LicenseType == license_type)
    if status_filter is not None:
        query = query.where(SoftwareLicense.LicenseStatus == status_filter)
    if software_id is not None:
        query = query.where(SoftwareLicense.SoftwareInfoID == software_id)

    # 排序并添加分页限制
    query = query.order_by(SoftwareLicense.LicenseID).offset(offset).limit(limit)

    result = await session.execute(query)  # 执行查询
    results_db: List[Tuple[SoftwareLicense, Optional[SoftwareInfo]]] = result.all()

    combined_results: List[SoftwareLicenseReadWithInfo] = []
    for license_db, info_db in results_db:
        license_read = SoftwareLicenseRead.model_validate(license_db)
        info_read = SoftwareInfoRead.model_validate(info_db) if info_db else None

        combined = SoftwareLicenseReadWithInfo(
            **license_read.model_dump(),
            software_info=info_read
        )
        combined_results.append(combined)

    return combined_results  # 返回组合后的结果


# 获取单个授权信息接口
@router.get("/{license_id}", response_model=SoftwareLicenseReadWithInfo)
async def get_single_license_manual_join(
    license_id: int,
    session: AsyncSession = Depends(get_session)
):

    license_db = await session.get(SoftwareLicense, license_id)  # 获取授权信息
    if not license_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到ID为 {license_id} 的软件授权"
        )

    info_read: Optional[SoftwareInfoRead] = None
    if license_db.SoftwareInfoID is not None:
        info_db = await session.get(SoftwareInfo, license_db.SoftwareInfoID)  # 获取对应的软件信息
        if info_db:
            info_read = SoftwareInfoRead.model_validate(info_db)

    license_read = SoftwareLicenseRead.model_validate(license_db)
    combined_result = SoftwareLicenseReadWithInfo(
        **license_read.model_dump(),
        software_info=info_read
    )

    return combined_result  # 返回组合后的结果