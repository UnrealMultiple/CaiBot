from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from caibot.db.model.user import User


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_by_id(self, _id: int) -> User | None:
        query = select(User).where(User.id == _id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> User | None:
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        return user
