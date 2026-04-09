from nonebot import on_command
from nonebot.adapters.milky import Bot, MessageSegment

from caibot import config, CommandMsg
from caibot.db import BanRecordRepo, BanRequestRepo
from caibot.db.model import BanRequest
from caibot.dependency import Args, Session, Group, GroupAdminPermission, User
from caibot.utils import ban_request_to_str, get_username, get_group_name

add_ban = on_command("添加云黑", force_whitespace=True)


@add_ban.handle()
async def _(bot: Bot, args: Args, session: Session, group: Group, user: User,
            permission: GroupAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="添加云黑",
        failed_msg="添加失败！",
        syntax="添加云黑 <QQ> <理由>"
    )

    if not permission:
        await add_ban.finish(
            msg.permission_denied()
        )

    if not user.allow_ban:
        await add_ban.finish(
            msg.failed(f"你已被禁止添加云黑\n"
                       f"申诉请加反馈群: {config.bot_admin_group_id}")
        )

    if not group.allow_ban:
        await add_ban.finish(
            msg.failed("本群已被禁止添加云黑\n"
                       f"申诉请加反馈群: {config.bot_admin_group_id}")
        )

    if len(args) < 2 or not args[0].isdigit():
        await add_ban.finish(
            msg.syntax_error()
        )

    target = int(args[0])
    reason = " ".join(args[1:])

    ban_record_repo = BanRecordRepo(session)
    ban_request_repo = BanRequestRepo(session)

    ban_record = await ban_record_repo.get_by_group_id_and_user_id(group.group_id, target)

    if ban_record is not None:
        await add_ban.finish(
            msg.failed(f"【{target}】已在本群的云黑名单中，无法再次添加")
        )

    ban_request = await ban_request_repo.get_by_group_id_and_user_id(group.group_id, target)
    if ban_request is not None:
        await add_ban.finish(
            msg.failed(f"【{target}】已在本群的云黑申请中，无法再次添加")
        )

    ban_request = BanRequest(
        user_id=target,
        reason=reason,
        creator_group_id=group.group_id,
        creator_user_id=user.user_id
    )

    ban_request = await ban_request_repo.create(ban_request)

    request_msg = await ban_request_to_str(ban_request, emoji=False)
    # noinspection PyUnresolvedReferences
    report_msg = MessageSegment.text(f"🙏云黑请求{request_msg}")

    await bot.send_group_message(group_id=config.bot_admin_group_id, message=report_msg)

    await add_ban.finish(
        msg.success(f"🙏云黑请求#{ban_request.id}\n"
                    f"已向反馈群提交申请！")
    )


del_ban = on_command("删除云黑", force_whitespace=True)


@del_ban.handle()
async def _(bot: Bot, args: Args, session: Session, group: Group, user: User,
            permission: GroupAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="删除云黑",
        failed_msg="删除失败！",
        syntax="删除云黑 <QQ>"
    )

    if not permission:
        await del_ban.finish(
            msg.permission_denied()
        )

    if len(args) != 1 or not args[0].isdigit():
        await del_ban.finish(
            msg.syntax_error()
        )

    target = int(args[0])

    ban_record_repo = BanRecordRepo(session)

    ban_record = await ban_record_repo.get_by_group_id_and_user_id(group.group_id, target)

    if ban_record is None:
        await del_ban.finish(
            msg.failed(f"【{target}】不在本群的云黑名单中")
        )

    await ban_record_repo.delete_by_group_id_and_user_id(group.group_id, target)

    target_username = await get_username(target, bot)
    group_name = await get_group_name(group.group_id, bot)
    report_msg = MessageSegment.text(f"❌删除云黑 {target_username} ({target})\n"
                                     f"删除群: {group_name} ({target})")

    await bot.send_group_message(group_id=config.bot_admin_group_id, message=report_msg)

    await del_ban.finish(
        msg.success(f"✅已删除【{target}】的云黑记录！")
    )
