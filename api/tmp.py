# main.py

# 导入FastAPI核心模块和依赖项
from fastapi import FastAPI, Depends, HTTPException, status, Query
# 导入SQLModel相关模块（ORM和数据库操作）
from sqlmodel import SQLModel, Session, select, create_engine, Field
# 类型提示相关模块
from typing import List, Optional
# Pydantic基础模型（用于数据验证）
from pydantic import BaseModel

# --------------------------
# 数据库配置部分
# --------------------------
# 定义数据库连接URL（这里使用SQLite内存数据库）
DATABASE_URL = "sqlite:///./software.db"
# 创建数据库引擎实例，echo=True表示输出SQL日志（生产环境建议关闭）
engine = create_engine(DATABASE_URL, echo=True)

# 依赖项：获取数据库会话
def get_session():
    # 使用上下文管理器确保会话正确关闭
    with Session(engine) as session:
        yield session  # 生成器方式提供会话

# --------------------------
# 数据模型定义部分
# --------------------------
# 软件信息基础模型（包含公共字段）
class SoftwareBase(SQLModel):
    软件显示名称: str = Field(min_length=1)  # 必填字段，最小长度1
    软件类型: Optional[int] = None        # 可选字段
    软件匹配规则: Optional[str] = None    # 可选字段

# 数据库表模型（继承基础模型并添加表特性）
class Software(SoftwareBase, table=True):
    __tablename__ = "software_info"  # 显式指定表名
    
    # 主键字段（SQLModel会自动识别primary_key=True）
    软件id: Optional[int] = Field(default=None, primary_key=True)

# 创建用请求模型（不需要ID字段）
class SoftwareCreate(SoftwareBase):
    pass  # 继承所有基础字段

# 读取用响应模型（包含ID字段）
class SoftwareRead(SoftwareBase):
    软件id: int  # 包含数据库生成的ID

# 更新用请求模型（所有字段可选）
class SoftwareUpdate(SQLModel):
    软件显示名称: Optional[str] = None
    软件类型: Optional[int] = None
    软件匹配规则: Optional[str] = None

# --------------------------
# FastAPI应用初始化
# --------------------------
# 创建FastAPI应用实例
app = FastAPI(title="软件管理系统API")

# 应用启动事件：创建数据库表
@app.on_event("startup")
def on_startup():
    # 调用SQLModel的元数据创建所有表（生产环境建议使用迁移工具）
    SQLModel.metadata.create_all(engine)

# --------------------------
# API端点实现部分
# --------------------------
# 创建软件条目
@app.post("/software/", 
         response_model=SoftwareRead,  # 指定响应模型
         status_code=status.HTTP_201_CREATED)  # 设置201状态码
def create_software(
    software: SoftwareCreate,          # 请求体参数（自动验证）
    session: Session = Depends(get_session)  # 注入数据库会话
):
    # 将请求数据转换为数据库模型
    db_software = Software.model_validate(software)
    # 添加到会话
    session.add(db_software)
    # 提交事务
    session.commit()
    # 刷新对象以获取数据库生成的ID等数据
    session.refresh(db_software)
    return db_software

# 获取软件列表（带分页和过滤）
@app.get("/software/", response_model=List[SoftwareRead])
def get_software_list(
    software_type: Optional[int] = Query(  # 查询参数：软件类型过滤
        None, 
        description="按软件类型筛选"
    ),
    page: int = Query(  # 分页页码
        1, 
        ge=1,  # 大于等于1
        description="页码（从1开始）"
    ),
    limit: int = Query(  # 每页数量
        20, 
        ge=1,  # 最少1条
        le=100,  # 最多100条
        description="每页数量"
    ),
    session: Session = Depends(get_session)
):
    # 计算分页偏移量
    offset = (page - 1) * limit
    # 基础查询语句
    query = select(Software)
    
    # 添加过滤条件（如果传入了软件类型）
    if software_type is not None:
        query = query.where(Software.软件类型 == software_type)
        
    # 执行查询并返回结果
    return session.exec(
        query.offset(offset).limit(limit)
    ).all()

# 获取单个软件详情
@app.get("/software/{software_id}", response_model=SoftwareRead)
def get_software(
    software_id: int,  # 路径参数
    session: Session = Depends(get_session)
):
    # 根据ID查询数据库
    software = session.get(Software, software_id)
    # 处理未找到情况
    if not software:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software not found"
        )
    return software

# 更新软件信息
@app.put("/software/{software_id}", response_model=SoftwareRead)
def update_software(
    software_id: int,
    software_data: SoftwareUpdate,  # 更新用请求体
    session: Session = Depends(get_session)
):
    # 获取现有数据
    db_software = session.get(Software, software_id)
    if not db_software:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Software not found"
        )
    
    # 将更新数据转换为字典（排除未设置字段）
    update_data = software_data.model_dump(exclude_unset=True)
    # 逐个字段更新
    for key, value in update_data.items():
        setattr(db_software, key, value)
    
    # 提交更改
    session.add(db_software)
    session.commit()
    session.refresh(db_software)
    return db_software

# 删除软件条目
@app.delete("/software/{software_id}", 
           status_code=status.HTTP_204_NO_CONTENT)
def delete_software(
    software_id: int,
    session: Session = Depends(get_session)
):
    # 查询要删除的记录
    software = session.get(Software, software_id)
    if not software:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software not found"
        )
    
    # 执行删除操作
    session.delete(software)
    session.commit()
    # 返回204 No Content（无响应体）