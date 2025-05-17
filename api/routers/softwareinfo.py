# 导入所需的模块和函数
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, SQLModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, AsyncGenerator
from models.softwareinfo import SoftwareInfo  # 引入软件信息模型
from schemas.softwareinfo import SoftwareInfoCreate, SoftwareInfoRead, SoftwareInfoUpdate  # 引入数据模式
from dependencies import get_session  # 引入获取数据库会话的依赖函数
from utils.jwt import get_current_user, get_current_admin  # 引入JWT验证相关函数

# 创建API路由实例，设置前缀和标签
router = APIRouter(
    prefix="/softwareinfo",
    tags=["softwareinfo"]
)

# 创建一个新的SoftwareInfo条目
@router.post("/", response_model=SoftwareInfoRead, status_code=status.HTTP_201_CREATED)
async def create_software(
    software: SoftwareInfoCreate,  # 请求体模型
    session: AsyncSession = Depends(get_session)  # 数据库会话依赖
):
    db_softwareinfo = SoftwareInfo.model_validate(software)  # 将请求体转换为数据库模型
    session.add(db_softwareinfo)  # 添加到数据库会话
    try:
        await session.commit()  # 提交删除事务
    except SQLAlchemyError as e:
        await session.rollback()  # 出错时回滚
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")  # 抛出自定义错误信息
    await session.refresh(db_softwareinfo)  # 刷新对象状态
    await session.refresh(db_softwareinfo)  # 刷新以获取新生成的ID等信息
    return db_softwareinfo  # 返回创建成功的响应

# 获取所有SoftwareInfo列表，支持按类型筛选、分页
@router.get("/", response_model=list[SoftwareInfoRead])
async def get_softwareinfo_list(
    softwareinfo_type: Optional[int] = Query(None, description="软件类型筛选"),  # 可选查询参数
    page: int = Query(1, ge=1, description="页码"),  # 当前页码
    limit: int = Query(20, ge=1, le=100, description="每页数量"),  # 每页数量限制
    session: AsyncSession = Depends(get_session)  # 数据库会话依赖
):
    offset = (page - 1) * limit  # 计算偏移量
    query = select(SoftwareInfo)  # 构建基础SQL查询

    if softwareinfo_type is not None:
        query = query.where(SoftwareInfo.SoftwareInfoType == softwareinfo_type)  # 如果有类型则添加过滤条件

    result = await session.execute(query.offset(offset).limit(limit).order_by(SoftwareInfo.SoftwareInfoID))  # 执行带分页及排序的查询

    return result.scalars().all()  # 返回结果列表

# 根据ID获取单个SoftwareInfo详情
@router.get("/{softwareinfo_id}", response_model=SoftwareInfoRead)
async def get_softwareinfo(
    softwareinfo_id: int,  # 路径参数
    session: AsyncSession = Depends(get_session)  # 数据库会话依赖
):
    result = await session.get(SoftwareInfo, softwareinfo_id)  # 查询指定ID的数据

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到软件信息")  # 未找到时抛出异常

    return result  # 返回查询结果

# 更新一个已存在的SoftwareInfo记录
@router.put("/{softwareinfo_id}", response_model=SoftwareInfoRead)
async def update_softwareinfo(
    softwareinfo_id: int,  # 路径参数
    software_data: SoftwareInfoUpdate,  # 更新内容
    session: AsyncSession = Depends(get_session)  # 数据库会话依赖
):
    db_softwareinfo = await session.get(SoftwareInfo, softwareinfo_id)  # 获取要更新的对象
    if not db_softwareinfo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到软件信息")  # 不存在则抛出异常

    update_data = software_data.model_dump(exclude_unset=True)  # 排除未设置的字段
    for key, value in update_data.items():
        setattr(db_softwareinfo, key, value)  # 动态更新属性

    session.add(db_softwareinfo)  # 添加回话并提交更改
    try:
        await session.commit()  # 提交删除事务
    except SQLAlchemyError as e:
        await session.rollback()  # 出错时回滚
        raise HTTPException(status_code=500, detail=f"数据库事务处理失败，错误: {e}")  # 抛出自定义错误信息
    await session.refresh(db_softwareinfo)  # 刷新对象状态
    return db_softwareinfo  # 返回更新后的数据

# 删除一个SoftwareInfo记录，需要管理员权限
@router.delete("/{softwareinfo_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=Depends(get_current_admin))
async def delete_softwareinfo(
    softwareinfo_id: int,
    session: AsyncSession = Depends(get_session)
):
    db_softwareinfo = await session.get(SoftwareInfo, softwareinfo_id)
    if not db_softwareinfo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到软件信息")

    await session.delete(db_softwareinfo)  # 准备删除操作
    try:
        await session.commit()  # 提交删除事务
    except SQLAlchemyError as e:
        await session.rollback()  # 出错时回滚
        raise HTTPException(status_code=500, detail=f"软件信息删除失败，可能有关联的数据存在： {e}")  # 抛出自定义错误信息