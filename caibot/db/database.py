from nonebot import get_plugin_config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from caibot.config import Config
from caibot.db.model.base import Base

_config = get_plugin_config(Config)

engine = create_async_engine(_config.db_url, echo=False, future=True, pool_pre_ping=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=True)


async def init_db():
    async with engine.begin() as conn:
        # WARNING: 此语句仅仅测试时使用
        # await conn.run_sync(lambda c: Base.metadata.drop_all(bind=c))
        await conn.run_sync(lambda c: Base.metadata.create_all(bind=c))
