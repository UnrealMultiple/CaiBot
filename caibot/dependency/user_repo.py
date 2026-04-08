from typing import Annotated

from nonebot.params import Depends

from caibot.db.user_repo import UserRepo
from caibot.dependency.session import Session


def get_user_repo(session: Session) -> UserRepo:
    return UserRepo(session)

UserRepo = Annotated[UserRepo, Depends(get_user_repo, use_cache=False)]