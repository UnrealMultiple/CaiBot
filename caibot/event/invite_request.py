from nonebot import on_request
from nonebot.adapters.milky.event import FriendRequestEvent, GroupInvitedJoinRequestEvent

from caibot.db import UserRepo, GroupRepo
from caibot.dependency import Session

friend_request = on_request()


@friend_request.handle()
async def _(event: FriendRequestEvent, session: Session):
    repo = UserRepo(session)

    user = await repo.get_by_user_id(event.data.initiator_id)

    if user is None or user.allow_ban:
        await event.accept()


group_request = on_request()


@group_request.handle()
async def _(event: GroupInvitedJoinRequestEvent, session: Session):
    user_repo = UserRepo(session)
    group_repo = GroupRepo(session)

    user = await user_repo.get_by_user_id(event.data.initiator_id)
    group = await group_repo.get_by_group_id(event.data.group_id)

    if (user is None or user.allow_ban) and (group is None or group.allow_ban):
        await event.accept()
