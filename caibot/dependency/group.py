from typing import Annotated

from nonebot.adapters.milky.event import GroupMessageEvent
from nonebot.params import Depends
from sqlalchemy.exc import IntegrityError

from caibot.db.model.group import Group
from caibot.dependency.group_repo import GroupRepo


async def get_group(event: GroupMessageEvent, group_repo: GroupRepo) -> Group:
    assert event.data.group is not None

    group = await group_repo.get_by_group_id(event.data.group.group_id)
    if group is None:
        try:
            group = Group(group_id=event.data.group.group_id)
            await group_repo.create(group)
        except IntegrityError:
            await group_repo.session.rollback()
            group = await group_repo.get_by_group_id(event.data.group.group_id)
            assert group is not None
    return group


Group = Annotated[Group, Depends(get_group, use_cache=False)]
