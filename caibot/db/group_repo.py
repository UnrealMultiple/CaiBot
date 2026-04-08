from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.functions import func

from caibot.db.model.group import Group


class GroupRepo:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_by_id(self, _id: int) -> Group | None:
        query = select(Group).where(Group.id == _id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_group_id(self, group_id: int) -> Group | None:
        query = select(Group).where(Group.group_id == group_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, group: Group) -> Group:
        self.session.add(group)
        await self.session.commit()
        return group

    async def update(self, group: Group) -> Group:
        self.session.add(group)
        await self.session.commit()
        return group

    async def count(self) -> int:
        query = select(func.count(Group.id)).select_from(Group)
        result = await self.session.execute(query)
        return result.scalar_one()
