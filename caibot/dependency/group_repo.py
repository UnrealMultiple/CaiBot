from typing import Annotated

from nonebot.params import Depends

from caibot.dependency.session import Session
from caibot.db import GroupRepo


def get_group_repo(session: Session) -> GroupRepo:
    return GroupRepo(session)


GroupRepo = Annotated[GroupRepo, Depends(get_group_repo, use_cache=False)]
