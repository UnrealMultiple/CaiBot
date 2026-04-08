from typing import Annotated

from nonebot.adapters.milky.event import GroupMessageEvent
from nonebot.params import Depends

from caibot.dependency.group_admin_repo import GroupAdminRepo


async def get_group_admins(event: GroupMessageEvent, group_admin_repo: GroupAdminRepo) -> list[int]:
   # noinspection PyUnresolvedReferences
   group_admins = await group_admin_repo.get_by_group_id(event.data.group.group_id)
   return [group_admin.user_id for group_admin in group_admins]

GroupAdmins = Annotated[list[int], Depends(get_group_admins, use_cache=False)]
