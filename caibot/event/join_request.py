from cachetools import TTLCache
from nonebot import on_request
from nonebot.adapters.milky import Bot
from nonebot.adapters.milky.event import GroupJoinRequestEvent

from caibot import config, CommandMsg
from caibot.db import BanRecordRepo, CheckLogRepo
from caibot.db.model import CheckLog
from caibot.dependency import Session
from caibot.utils import ban_record_to_str, get_username

join_request = on_request()

_handled_cache: TTLCache = TTLCache(maxsize=1024, ttl=60 * 60)


@join_request.handle()
async def _(bot: Bot, event: GroupJoinRequestEvent, session: Session):
    repo = BanRecordRepo(session)

    ban_records = await repo.get_by_user_id(event.data.initiator_id)

    if len(ban_records) < 2 and not any([ban for ban in ban_records if ban.creator_group_id == event.data.group_id]):
        return

    await event.reject(
        reason=f"你在云黑名单中，申诉请加: {config.bot_admin_group_id}"
    )

    log_repo = CheckLogRepo(session)
    await log_repo.create(
        CheckLog(
            user_id=event.data.initiator_id,
            group_id=event.data.group_id,
            rejected=True,
        )
    )

    msg = CommandMsg(
        user_id=None,
        title="云黑名单",
        sub_title="拒绝加群"
    )

    result: list[str] = []
    for ban_record in ban_records:
        result.append(await ban_record_to_str(ban_record))

    username = await get_username(event.data.initiator_id, bot)

    cache_key = (event.data.initiator_id, event.data.group_id)
    if cache_key in _handled_cache:
        return
    _handled_cache[cache_key] = True

    await bot.send_group_message(
        group_id=event.data.group_id,
        message=msg.success(
            f"❌已拒绝{username} ({event.data.initiator_id})的加群申请:\n" +
            "\n".join(result)
        )
    )
