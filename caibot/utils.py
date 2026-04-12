from nonebot.adapters.milky import Bot
from nonebot.exception import ActionFailed

from caibot.db.model import BanRequest, BanRecord

from cachetools import TTLCache
import nonebot

user_cache = TTLCache(maxsize=1000, ttl=60 * 60 * 24)
group_cache = TTLCache(maxsize=1000, ttl=60 * 60 * 48)


async def get_username(user_id: int, bot: Bot | None = None) -> str:
    if user_id == -1:
        return "无记录"

    if user_id in user_cache:
        return user_cache[user_id]

    if bot is None:
        bot: Bot = nonebot.get_bot()

    try:
        profile = await bot.get_user_profile(user_id=user_id)
        nickname = profile.nickname
        user_cache[user_id] = nickname
        return nickname
    except ActionFailed:
        user_cache[user_id] = "未知用户"
        return "未知用户"


async def get_group_name(group_id: int, bot: Bot | None = None) -> str:
    if group_id == -1:
        return "无记录"

    if group_id in group_cache:
        return group_cache[group_id]

    if bot is None:
        bot: Bot = nonebot.get_bot()

    try:
        profile = await bot.get_group_info(group_id=group_id)
        group_name = profile.group_name
        group_cache[group_id] = group_name
        return group_name
    except ActionFailed:
        group_cache[group_id] = "未知群聊"
        return "未知群聊"


async def ban_request_to_str(ban_request: BanRequest, emoji: bool = True) -> str:
    bot: Bot = nonebot.get_bot()
    target_username = await get_username(ban_request.user_id, bot)
    creator_group_name = await get_group_name(ban_request.creator_group_id, bot)
    creator_username = await get_username(ban_request.creator_user_id, bot)

    tag = f"#{ban_request.id}" if not emoji else f"#⃣[{ban_request.id}]"

    return (f"{tag} {target_username} ({ban_request.user_id})\n"
            f"管理员: {creator_username} ({ban_request.creator_user_id})\n"
            f"添加群: {creator_group_name} ({ban_request.creator_group_id})\n"
            f"理由: {ban_request.reason}")


async def ban_record_to_str(ban_record: BanRecord, emoji: bool = True) -> str:
    bot: Bot = nonebot.get_bot()
    creator_group_name = await get_group_name(ban_record.creator_group_id, bot)
    tag = f"#{ban_record.id}" if not emoji else f"#⃣[{ban_record.id}]"
    return f"{tag} {creator_group_name}: {ban_record.reason} ({ban_record.time.date().isoformat()})"


async def ban_record_to_detail(ban_record: BanRecord, emoji: bool = True) -> str:
    bot: Bot = nonebot.get_bot()
    target_username = await get_username(ban_record.user_id, bot)
    creator_group_name = await get_group_name(ban_record.creator_group_id, bot)
    creator_username = await get_username(ban_record.creator_user_id, bot)
    reviewer_name = await get_username(ban_record.reviewer_id, bot)
    tag = f"#{ban_record.id}" if not emoji else f"#⃣[{ban_record.id}]"
    return (f"{tag} {target_username} ({ban_record.user_id})\n"
            f"管理员: {creator_username} ({ban_record.creator_user_id})\n"
            f"添加群: {creator_group_name} ({ban_record.creator_group_id})\n"
            f"审核人: {reviewer_name} ({ban_record.reviewer_id})\n"
            f"时间: {ban_record.time.date().isoformat()}\n"
            f"理由: {ban_record.reason}")
