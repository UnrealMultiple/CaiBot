from nonebot import on_command
from nonebot.adapters.milky import Bot, MessageSegment

from caibot import CommandMsg
from caibot.db import BanRequestRepo, BanRecordRepo
from caibot.db.model import BanRecord
from caibot.dependency import Session, BotAdminPermission, User, Args
from caibot.utils import ban_request_to_str, get_username

request_list = on_command("审核列表", force_whitespace=True)


@request_list.handle()
async def _(session: Session, user: User,
            permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="云黑审核",
    )

    if not permission:
        await request_list.finish(
            msg.permission_denied()
        )

    repo = BanRequestRepo(session)

    requests = await repo.get_all_pending()

    if len(requests) == 0:
        await request_list.finish(
            msg.failed("当前没有待审核的云黑捏~")
        )

    result: list[str] = []

    for request in requests:
        request_msg = await ban_request_to_str(request)
        result.append(request_msg)

    await request_list.finish(
        msg.success("\n\n".join(result))
    )


approve = on_command("云黑批准", force_whitespace=True)


@approve.handle()
async def _(bot: Bot, session: Session, args: Args, user: User,
            permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="云黑审核",
        syntax="云黑批准 <请求ID>"
    )

    if not permission:
        await approve.finish(
            msg.permission_denied()
        )

    if len(args) != 1 or not args[0].isdigit():
        await approve.finish(
            msg.syntax_error()
        )

    request_id = int(args[0])

    request_repo = BanRequestRepo(session)
    record_repo = BanRecordRepo(session)

    request = await request_repo.get_by_id(request_id)

    if request is None:
        await approve.finish(
            msg.failed("请求ID无效！")
        )
        return

    if request.reviewed:
        await approve.finish(
            msg.failed("该请求已被审核过了！")
        )

    request = await request_repo.review_request(request, approve=True, reviewer_user_id=user.user_id)

    record = BanRecord(
        user_id=request.user_id,
        reason=request.reason,
        reviewer_id=request.reviewer_id,
        creator_user_id=request.creator_user_id,
        creator_group_id=request.creator_group_id,
    )

    _ = await record_repo.create(record)

    target_username = await get_username(request.user_id, bot)

    report_msg = CommandMsg(
        user_id=request.creator_user_id,
        title="云黑审核",
    )

    await bot.send_group_message(group_id=request.creator_group_id, message=report_msg.success(
        f"✅云黑请求#{request.id}已批准！\n"
        f"目标: {target_username} ({request.user_id})"
    ))

    await approve.finish(
        msg.success(f"✅已批准#{request.id}！")
    )

reject = on_command("云黑驳回", force_whitespace=True)


@reject.handle()
async def _(bot: Bot, session: Session, args: Args, user: User,
            permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="云黑审核",
        syntax="云黑驳回 <请求ID>"
    )

    if not permission:
        await reject.finish(
            msg.permission_denied()
        )

    if len(args) != 2 or not args[0].isdigit():
        await reject.finish(
            msg.syntax_error()
        )

    request_id = int(args[0])
    reason = args[1]

    request_repo = BanRequestRepo(session)

    request = await request_repo.get_by_id(request_id)

    if request is None:
        await approve.finish(
            msg.failed("请求ID无效！")
        )
        return

    if request.reviewed:
        await approve.finish(
            msg.failed("该请求已被审核过了！")
        )

    request = await request_repo.review_request(request, approve=False, reviewer_user_id=user.user_id)

    target_username = await get_username(request.user_id, bot)

    report_msg = CommandMsg(
        user_id=request.creator_user_id,
        title="云黑审核",
    )

    await bot.send_group_message(group_id=request.creator_group_id, message=report_msg.success(
        f"❌云黑请求#{request.id}已驳回！\n"
        f"目标: {target_username} ({request.user_id})\n"
        f"原因: {reason}"
    ))

    await approve.finish(
        msg.success(f"❌已驳回#{request.id}！")
    )