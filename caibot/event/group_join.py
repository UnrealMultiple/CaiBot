from nonebot.adapters.milky import Bot
from nonebot.plugin.on import on_notice
from nonebot.adapters.milky.event import GroupMemberIncreaseEvent

from caibot import CommandMsg
from caibot.constants import TSHOCK_GROUP_ID, CAIBOT_GUIDE
from caibot.db import BanRecordRepo, CheckLogRepo
from caibot.db.model import CheckLog
from caibot.dependency import Session
from caibot.utils import ban_record_to_str, get_username

group_join = on_notice()


@group_join.handle()
async def _(bot: Bot, event: GroupMemberIncreaseEvent, session: Session):
    if event.data.user_id == bot.self_id:
        msg = CommandMsg(
            user_id=event.data.user_id,
            title="欢迎使用CaiBot"
        )
        await bot.send_group_message(
            group_id=event.data.group_id,
            message=msg.success(CAIBOT_GUIDE)
        )
        return

    if event.data.group_id == TSHOCK_GROUP_ID:
        msg = CommandMsg(
            user_id=event.data.user_id,
            title="欢迎加入TShock官方群"
        )
        await bot.send_group_message(
            group_id=event.data.group_id,
            message=msg.success(CAIBOT_GUIDE)
        )
        return

    repo = BanRecordRepo(session)

    ban_records = await repo.get_by_user_id(event.data.user_id)

    msg = CommandMsg(
        user_id=event.data.user_id,
        title="云黑名单"
    )

    if len(ban_records) == 0:
        await bot.send_group_message(
            group_id=event.data.group_id,
            message=msg.success(
                f"✅没有检测到云黑记录({event.data.user_id})!"
            )
        )
        return

    result: list[str] = []
    for ban_record in ban_records:
        result.append(await ban_record_to_str(ban_record))

    username = await get_username(event.data.user_id, bot)

    await bot.send_group_message(
        group_id=event.data.group_id,
        message=msg.success(
            f"❌检测到{username} ({event.data.user_id})有{len(ban_records)}条云黑记录:\n" +
            "\n".join(result)
        )
    )

    log_repo = CheckLogRepo(session)
    await log_repo.create(
        CheckLog(
            user_id=event.data.user_id,
            group_id=event.data.group_id,
            rejected=False,
        )
    )
