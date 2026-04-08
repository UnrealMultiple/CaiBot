import asyncio
from typing import Annotated

import nonebot
from cachetools import TTLCache
from nonebot.adapters.milky import Bot
from nonebot.adapters.milky.event import GroupMessageEvent
from nonebot.params import Depends

from caibot import config
from caibot.dependency.group import Group
from caibot.dependency.group_admins import GroupAdmins
from caibot.dependency.user import User

_bot_admin_cache: TTLCache = TTLCache(maxsize=1, ttl=60 * 60 * 24)
_bot_admin_cache_lock = asyncio.Lock()
BOT_ADMIN_CACHE_KEY = "admins"


async def _get_bot_admin_set(bot: Bot) -> set[int]:
    if BOT_ADMIN_CACHE_KEY in _bot_admin_cache:
        nonebot.logger.debug(f"Hit bot_admin_cache: {_bot_admin_cache[BOT_ADMIN_CACHE_KEY]}")
        return _bot_admin_cache[BOT_ADMIN_CACHE_KEY]

    async with _bot_admin_cache_lock:
        if BOT_ADMIN_CACHE_KEY in _bot_admin_cache:
            return _bot_admin_cache[BOT_ADMIN_CACHE_KEY]

        members = await bot.get_group_member_list(group_id=config.bot_admin_group_id, no_cache=True)
        _bot_admin_cache[BOT_ADMIN_CACHE_KEY] = {member.user_id for member in members if
                                                 member.role in ["admin", "owner"]}
        nonebot.logger.debug(f"Hit bot_admin_cache: {_bot_admin_cache}")
        return _bot_admin_cache[BOT_ADMIN_CACHE_KEY]


async def check_bot_admin(bot: Bot, user: User) -> bool:
    return user.user_id in await _get_bot_admin_set(bot)


async def check_common(bot: Bot, group: Group, user: User) -> bool:
    base_allowed = user.allow_use_bot and group.allow_use_bot
    return base_allowed or await check_bot_admin(bot, user)


async def check_group_admin(
        bot: Bot,
        event: GroupMessageEvent,
        group: Group,
        user: User,
        group_admins: GroupAdmins
) -> bool:
    # noinspection PyUnresolvedReferences
    is_group_admin = event.data.sender.role in ("owner", "admin")
    return ((await check_common(bot, group, user) and (
            is_group_admin or event.data.sender.user_id in group_admins))
            or await check_bot_admin(bot, user))


async def check_group_owner(
        bot: Bot,
        event: GroupMessageEvent,
        group: Group,
        user: User,
) -> bool:
    # noinspection PyUnresolvedReferences
    is_owner = event.data.sender.role == "owner"
    return (await check_common(bot, group, user) and is_owner) or await check_bot_admin(bot, user)


CommonPermission = Annotated[bool, Depends(check_common)]
GroupAdminPermission = Annotated[bool, Depends(check_group_admin)]
GroupOwnerPermission = Annotated[bool, Depends(check_group_owner)]
BotAdminPermission = Annotated[bool, Depends(check_bot_admin)]
