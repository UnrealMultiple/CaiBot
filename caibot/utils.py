import nonebot
from nonebot.adapters.milky import Bot
from nonebot.exception import ActionFailed

from caibot.db.model import BanRequest


async def get_username(user_id: int, bot: Bot | None = None) -> str:
    if bot is None:
        bot: Bot = nonebot.get_bot()
    try:
        profile = await bot.get_user_profile(user_id=user_id)
        return profile.nickname
    except ActionFailed:
        return "未知用户"


async def get_group_name(user_id: int, bot: Bot | None = None) -> str:
    if bot is None:
        bot: Bot = nonebot.get_bot()
    try:
        profile = await bot.get_group_info(group_id=user_id)
        return profile.group_name
    except ActionFailed:
        return "未知群聊"


async def ban_request_to_str(ban_request: BanRequest) -> str:
    bot: Bot = nonebot.get_bot()
    target_username = await get_username(ban_request.user_id, bot)
    creator_group_name = await get_group_name(ban_request.creator_group_id, bot)
    creator_username = await get_username(ban_request.creator_user_id, bot)

    return (f"#{ban_request.id} {target_username} ({ban_request.user_id})\n"
            f"管理员: {creator_username} ({ban_request.creator_user_id})\n"
            f"添加群: {creator_group_name} ({ban_request.creator_group_id})\n"
            f"理由: {ban_request.reason}")
