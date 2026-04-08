from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from caibot.db.model import BanRequest


class BanRequestRepo:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_by_id(self, _id: int) -> BanRequest | None:
        query = select(BanRequest).where(BanRequest.id == _id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_group_id_and_user_id(self, group_id: int, user_id: int) -> BanRequest | None:
        query = select(BanRequest).where(BanRequest.user_id == user_id, BanRequest.creator_group_id == group_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_pending(self) -> list[BanRequest]:
        query = select(BanRequest).where(BanRequest.reviewed==False).order_by(BanRequest.id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def review_request(self,ban_request: BanRequest, approve: bool, reviewer_user_id: int) -> BanRequest:
        ban_request.approve = approve
        ban_request.reviewed = True
        ban_request.reviewer_user_id = reviewer_user_id
        self.session.add(ban_request)
        await self.session.commit()

        return ban_request


    async def create(self, ban_request: BanRequest) -> BanRequest:
        self.session.add(ban_request)
        await self.session.commit()
        return ban_request
