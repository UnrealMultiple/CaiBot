from typing import Annotated

from nonebot.params import Depends

from caibot.db.group_admin_repo import GroupAdminRepo
from caibot.dependency.session import Session


def get_group_admin_repo(session: Session) -> GroupAdminRepo:
    return GroupAdminRepo(session)


GroupAdminRepo = Annotated[GroupAdminRepo, Depends(get_group_admin_repo, use_cache=False)]
