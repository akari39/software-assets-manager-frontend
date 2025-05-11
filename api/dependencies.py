# api/dependencies.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker # 建议使用 async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator
import traceback
import logging # <--- 1. 导入标准 logging 模块

# <--- 2. 获取一个 logger 实例 (通常以当前模块命名)
logger = logging.getLogger(__name__)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    from main import engine # 假设 engine 在 main.py 中定义并导入
    
    # 使用 async_sessionmaker (SQLAlchemy 1.4.27+ 和 2.0+)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e: # 当端点代码使用 session 并抛出 SQLAlchemyError 时，会在这里捕获
            await session.rollback()
            print("\n\n!!!!!!!!!!!!!! SQLAlchemyError Caught in get_session !!!!!!!!!!!!!!")
            traceback.print_exc()  # 打印原始 SQLAlchemyError 的 Traceback
            # <--- 3. 使用配置好的 logger 实例，并添加 exc_info=True 获取异常信息
            logger.error(f"Database session error occurred (SQLAlchemyError): {e}", exc_info=True)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
            raise HTTPException(status_code=500, detail=f"Database session error occurred: {str(e)}")
        except Exception as e: # 捕获其他可能的异常
            # 对于非 SQLAlchemyError，是否回滚以及会话状态需要谨慎处理
            # await session.rollback() # 可能不需要或会话已无效
            print("\n\n!!!!!!!!!!!!!! Generic Exception Caught in get_session !!!!!!!!!!!!!!")
            traceback.print_exc() # 打印此 Exception 的 Traceback
            # <--- 3. 使用配置好的 logger 实例
            logger.error(f"Unexpected error in session management: {e}", exc_info=True)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
            raise HTTPException(status_code=500, detail=f"Unexpected error in session management: {str(e)}")