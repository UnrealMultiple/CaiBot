from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from caibot.db.model import CheckLog


class CheckLogRepo:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_by_user_id(self, user_id: int) -> list[CheckLog]:
        query = select(CheckLog).where(CheckLog.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_group_id(self, group_id: int) -> list[CheckLog]:
        query = select(CheckLog).where(CheckLog.group_id == group_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, check_log: CheckLog) -> CheckLog:
        self.session.add(check_log)
        await self.session.commit()
        return check_log

    async def count_all(self) -> int:
        query = select(func.count(CheckLog.id)).select_from(CheckLog)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def count_all_reject(self) -> int:
        query = select(func.count(CheckLog.id)).where(CheckLog.rejected).select_from(CheckLog)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def count_group(self, group_id: int) -> int:
        query = select(func.count(CheckLog.id)).where(CheckLog.group_id == group_id).select_from(CheckLog)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def count_group_reject(self, group_id: int) -> int:
        query = select(func.count(CheckLog.id)).where(CheckLog.group_id == group_id, CheckLog.rejected).select_from(
            CheckLog)
        result = await self.session.execute(query)
        return result.scalar_one()
