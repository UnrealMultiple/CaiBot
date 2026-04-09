from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from caibot.db.model import GroupAdmin


class GroupAdminRepo:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(self, group_admin: GroupAdmin) -> GroupAdmin:
        self.session.add(group_admin)
        await self.session.commit()
        return group_admin

    async def get_by_group_id(self, group_id: int) -> list[GroupAdmin]:
        query = select(GroupAdmin).where(GroupAdmin.group_id == group_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_group_id_and_user_id(self, group_id: int, user_id: int) -> GroupAdmin | None:
        query = select(GroupAdmin).where(GroupAdmin.group_id == group_id, GroupAdmin.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, group_id: int, user_id: int) -> None:
        await self.session.execute(
            delete(GroupAdmin).where(GroupAdmin.group_id == group_id, GroupAdmin.user_id == user_id)
        )
        await self.session.commit()
