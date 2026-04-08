from typing import Annotated

from nonebot.adapters.milky.event import MessageEvent
from nonebot.params import Depends
from sqlalchemy.exc import IntegrityError

from caibot.db.model.user import User
from caibot.dependency.user_repo import UserRepo


async def get_user(event: MessageEvent, user_repo: UserRepo) -> User:
    user = await user_repo.get_by_user_id(event.data.sender.user_id)
    if user is None:
        try:
            user = User(user_id=event.data.sender.user_id)
            await user_repo.create(user)
        except IntegrityError:
            await user_repo.session.rollback()
            user = await user_repo.get_by_user_id(event.data.sender.user_id)
            assert user is not None
    return user


User = Annotated[User, Depends(get_user, use_cache=False)]
