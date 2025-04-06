from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, SQLModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, AsyncGenerator

# 定義數據模型 (只在路由文件內部使用)
class SoftwareInfoBase(SQLModel):
    SoftwareInfoName: str = Field(min_length=1)
    SoftwareInfoType: Optional[int] = None
    SoftwareInfoMatchRule: Optional[str] = None
    
class SoftwareInfo(SoftwareInfoBase, table=True):
    __tablename__ = "software_info" 
    SoftwareInfoID: Optional[int] = Field(default=None, primary_key=True)

# 請求/響應模型
class SoftwareInfoCreate(SoftwareInfoBase):
    pass

class SoftwareInfoRead(SoftwareInfoBase):
    SoftwareInfoID: int

class SoftwareInfoUpdate(SQLModel):
    SoftwareInfoName: Optional[str] = None
    SoftwareInfoType: Optional[int] = None
    SoftwareInfoMatchRule: Optional[str] = None

# 創建路由實例
router = APIRouter(
    prefix="/softwareinfo",
    tags=["softwareinfo"]
)

# 依賴注入 (內部定義)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    from main import engine
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session




# 路由處理函數
@router.post("/", response_model=SoftwareInfoRead, status_code=status.HTTP_201_CREATED)
async def create_software(
    software: SoftwareInfoCreate,
    session: AsyncSession = Depends(get_session)
):
    db_softwareinfo = SoftwareInfo.model_validate(software)
    session.add(db_softwareinfo)
    await session.commit()
    await session.refresh(db_softwareinfo)
    return db_softwareinfo

@router.get("/",response_model = list[SoftwareInfoRead])
async def get_softwareinfo_list(
    softwareinfo_type: Optional[int] = Query(
        None,
        description="按軟件類型篩選"
    ),
    page: int = Query(
        1,
        ge = 1,
        description="頁碼"
    ),
    limit: int = Query(
        20,
        ge = 1,
        le = 100,
        description="每頁數量"
    ),
    session: AsyncSession = Depends(get_session)
):
    offset = (page - 1) * limit
    query = select(SoftwareInfo)

    if softwareinfo_type is not None:
        query = query.where(SoftwareInfo.SoftwareInfoType == softwareinfo_type)

    result = await session.execute(
        query.offset(offset).limit(limit).order_by(SoftwareInfo.SoftwareInfoID) #使用Order_by指定主鍵排序進行查找
    )

    return result.scalars().all()

@router.get("/{softwareinfo_id}",response_model = SoftwareInfoRead)
async def get_softwareinfo(
    softwareinfo_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.get(SoftwareInfo, softwareinfo_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SoftwareInfo not found"
        )
    
    return result

@router.put("/{softwareinfo_id}",response_model = SoftwareInfoRead)
async def update_softwareinfo(
    softwareinfo_id: int,
    software_data: SoftwareInfoUpdate,
    session: AsyncSession = Depends(get_session)
):
    db_softwareinfo = await session.get(SoftwareInfo, softwareinfo_id)
    if not db_softwareinfo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SoftwareInfo not found"
        )
    update_data = software_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_softwareinfo, key, value)

    session.add(db_softwareinfo)
    await session.commit()
    await session.refresh(db_softwareinfo)
    return db_softwareinfo

@router.delete("/{softwareinfo_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_softwareinfo(
    softwareinfo_id: int,
    session: AsyncSession = Depends(get_session)
):
    db_softwareinfo = await session.get(SoftwareInfo, softwareinfo_id)
    if not db_softwareinfo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SoftwareInfo not found"
        )
    
    await session.delete(db_softwareinfo)
    try:
        await session.commit()
    except  SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="数据库操作失败")