from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    生成一个异步数据库会话（session）的依赖项，用于 FastAPI 的依赖注入。
    使用 async_sessionmaker 创建异步会话，适用于 SQLAlchemy 2.0+ 的异步模式。
    """
    from main import engine

    # 创建异步 session 工厂
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,         # 绑定到数据库引擎
        class_=AsyncSession, # 指定使用 AsyncSession 类型
        expire_on_commit=False  # 提交后不使实例过期，方便后续访问数据
    )

    # 使用 async with 启动一个异步会话
    async with AsyncSessionLocal() as session:
        try:
            # 提供会话给调用者（例如路由函数），在此处 yield 返回一个 Session 实例
            yield session
        except SQLAlchemyError as e:
            # 捕获所有 SQLAlchemy 相关异常，进行回滚处理
            await session.rollback()
            # 抛出 HTTP 异常，返回 500 错误和异常信息
            raise HTTPException(status_code=500, detail=f"Database session error occurred: {str(e)}")
        except Exception as e:
            # 捕获其他未知异常，抛出通用的服务器错误
            raise HTTPException(status_code=500, detail=f"Unexpected error in session management: {str(e)}")