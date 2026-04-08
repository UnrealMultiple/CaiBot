from typing import Annotated, AsyncGenerator

from nonebot.params import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from caibot.db.database import async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


Session = Annotated[AsyncSession, Depends(get_session, use_cache=False)]