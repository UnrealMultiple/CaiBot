from nonebot import on_command
from nonebot.adapters.milky import Bot

from caibot import CommandMsg
from caibot.db.model.group_admin import GroupAdmin
from caibot.dependency import Args, Group, User, GroupOwnerPermission, GroupAdminRepo
from caibot.utils import get_username

add_group_admin = on_command("添加管理", force_whitespace=True)


@add_group_admin.handle()
async def _(bot: Bot, args: Args, group: Group, user: User,
            permission: GroupOwnerPermission, group_admin_repo: GroupAdminRepo):
    msg = CommandMsg(
        user_id=user.user_id,
        title="添加管理",
        failed_msg="添加失败！",
        syntax="添加管理 <QQ>"
    )

    if not permission:
        await add_group_admin.finish(msg.permission_denied())

    if len(args) != 1 or not args[0].isdigit():
        await add_group_admin.finish(msg.syntax_error())

    target = int(args[0])

    existing = await group_admin_repo.get_by_group_id_and_user_id(group.group_id, target)
    if existing is not None:
        await add_group_admin.finish(msg.failed(f"【{target}】已是本群Bot管理员！"))

    record = GroupAdmin(user_id=target, group_id=group.group_id)
    await group_admin_repo.create(record)

    target_name = await get_username(target, bot)
    await add_group_admin.finish(
        msg.success(f"✅已将{target_name} ({target})设为本群Bot管理员")
    )


del_group_admin = on_command("删除管理", force_whitespace=True)


@del_group_admin.handle()
async def _(bot: Bot, args: Args, group: Group, user: User,
            permission: GroupOwnerPermission, group_admin_repo: GroupAdminRepo):
    msg = CommandMsg(
        user_id=user.user_id,
        title="删除管理",
        failed_msg="删除失败！",
        syntax="删除管理 <QQ>"
    )

    if not permission:
        await del_group_admin.finish(msg.permission_denied())

    if len(args) != 1 or not args[0].isdigit():
        await del_group_admin.finish(msg.syntax_error())

    target = int(args[0])

    existing = await group_admin_repo.get_by_group_id_and_user_id(group.group_id, target)
    if existing is None:
        await del_group_admin.finish(msg.failed(f"【{target}】不是本群Bot管理员！"))

    await group_admin_repo.delete(group.group_id, target)

    target_name = await get_username(target, bot)
    await del_group_admin.finish(
        msg.success(f"✅已移除{target_name} ({target})的本群Bot管理员权限")
    )

