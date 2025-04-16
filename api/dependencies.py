from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    # 假設 engine 在 main.py 中定義並導入
    from .main import engine # 需要確保可以從main導入engine
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            # 可以选择在这里记录日志
            # logger.error(f"Database session error: {e}")
            raise HTTPException(status_code=500, detail=f"Database error occurred: {e}")
        finally:
            await session.close()