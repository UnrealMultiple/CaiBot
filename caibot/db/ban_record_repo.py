from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from caibot.db.model.ban_record import BanRecord


class BanRecordRepo:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_by_id(self, _id: int) -> BanRecord | None:
        query = select(BanRecord).where(BanRecord.id == _id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[BanRecord]:
        query = select(BanRecord).where(BanRecord.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_group_id(self, group_id: int) -> list[BanRecord]:
        query = select(BanRecord).where(BanRecord.creator_group_id == group_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_group_id_and_user_id(self, group_id: int, user_id: int) -> BanRecord | None:
        query = select(BanRecord).where(BanRecord.creator_group_id == group_id, BanRecord.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, ban_record: BanRecord) -> BanRecord:
        self.session.add(ban_record)
        await self.session.commit()
        return ban_record

    async def update(self, ban_record: BanRecord) -> BanRecord:
        self.session.add(ban_record)
        await self.session.commit()
        return ban_record

    async def count_all(self) -> int:
        query = select(func.count(BanRecord.id)).select_from(BanRecord)
        result = await self.session.execute(query)
        return result.scalar_one()
