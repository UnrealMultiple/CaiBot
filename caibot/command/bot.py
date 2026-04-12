from nonebot import on_command
from nonebot.adapters.milky import Bot
from nonebot.adapters.milky.event import MessageEvent, GroupMessageEvent

from caibot import CommandMsg
from caibot.db import CheckLogRepo, GroupRepo
from caibot.dependency import Args, Session, BotAdminPermission, User

about_bot = on_command("关于", force_whitespace=True)


@about_bot.handle()
async def _(event: MessageEvent, session: Session):
    msg = CommandMsg(
        user_id=event.data.sender.user_id if isinstance(event, GroupMessageEvent) else None,
        title="关于"
    )

    check_log_repo = CheckLogRepo(session)
    group_repo = GroupRepo(session)

    total_group = await group_repo.count()
    total_check = await check_log_repo.count_all()
    total_reject = await check_log_repo.count_all_reject()
    assert event.data.group is not None
    group_check = await check_log_repo.count_group(event.data.group.group_id)
    group_reject = await check_log_repo.count_group_reject(event.data.group.group_id)

    await about_bot.finish(
        msg.success(f'📖CaiBot v0.1.0\n'
                    f'🎉开发者: Cai\n'
                    f'✨感谢: \n'
                    f'迅猛龙 [提供服务器]\n'
                    f'🙏反馈群: 991556763\n'
                    f'⚡当前已加入{total_group}个群\n'
                    f'全局: 检查{total_check}次 / 拒绝{total_reject}人\n'
                    f'本群: 检查{group_check}次 / 拒绝{group_reject}人\n'
                    f'Powered by Nonebot2')
    )


look_for = on_command("lookfor", force_whitespace=True)


@look_for.handle()
async def _(bot: Bot, user: User, args: Args, permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="搜索",
        syntax="lookfor <QQ>"
    )

    if not permission:
        await look_for.finish(
            msg.permission_denied()
        )

    if len(args) != 1 or not args[0].isdigit():
        await look_for.finish(
            msg.syntax_error()
        )

    target = int(args[0])

    group_list = await bot.get_group_list()
    result: list[str] = []

    for group in group_list:
        member_list = await bot.get_group_member_list(group_id=group.group_id)
        for member in member_list:
            if member.user_id == target:
                result.append(f"{group.group_name} ({group.group_id})")

    if len(result) == 0:
        await look_for.finish(
            msg.success(f"【{target}】不在任何CaiBot管理的群中")
        )

    await look_for.finish(
        msg.success(
            f"【{target}】在以下群中:\n" +
            "\n".join(result)
        )
    )
