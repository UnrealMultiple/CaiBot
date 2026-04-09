from nonebot import on_command
from nonebot.adapters.milky import Bot

from caibot import CommandMsg, config
from caibot.db import BanRecordRepo, UserRepo as DbUserRepo, GroupRepo as DbGroupRepo
from caibot.db.model.user import User as UserModel
from caibot.db.model.group import Group as GroupModel
from caibot.dependency import Args, Session, User, BotAdminPermission
from caibot.utils import get_username, get_group_name

group_ban_delete = on_command("群云黑删除", force_whitespace=True)


@group_ban_delete.handle()
async def _(bot: Bot, args: Args, session: Session, user: User, permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="群云黑删除",
        failed_msg="删除失败！",
        syntax="群云黑删除 <云黑ID>"
    )

    if not permission:
        await group_ban_delete.finish(msg.permission_denied())

    if len(args) != 1 or not args[0].isdigit():
        await group_ban_delete.finish(msg.syntax_error())

    record_id = int(args[0])
    ban_record_repo = BanRecordRepo(session)
    record = await ban_record_repo.get_by_id(record_id)

    if record is None:
        await group_ban_delete.finish(msg.failed(f"未找到云黑记录 #{record_id}"))
        return

    target_username = await get_username(record.user_id, bot)
    group_name = await get_group_name(record.creator_group_id, bot)

    await ban_record_repo.delete_by_id(record_id)

    await group_ban_delete.finish(
        msg.success(f"✅已删除云黑记录 #{record_id}\n"
                    f"目标: {target_username} ({record.user_id})\n"
                    f"来源群: {group_name} ({record.creator_group_id})")
    )


async def _get_or_create_user(user_id: int, session) -> UserModel:
    repo = DbUserRepo(session)
    db_user = await repo.get_by_user_id(user_id)
    if db_user is None:
        db_user = UserModel(user_id=user_id)
        db_user = await repo.create(db_user)
    return db_user


async def _get_or_create_group(group_id: int, session) -> GroupModel:
    repo = DbGroupRepo(session)
    db_group = await repo.get_by_group_id(group_id)
    if db_group is None:
        db_group = GroupModel(group_id=group_id)
        db_group = await repo.create(db_group)
    return db_group


ban_user_bot = on_command("禁止用户", force_whitespace=True)


@ban_user_bot.handle()
async def _(bot: Bot, args: Args, session: Session, user: User, permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="禁止用户",
        failed_msg="操作失败！",
        syntax="禁止用户 <QQ> <禁止|解禁>"
    )

    if not permission:
        await ban_user_bot.finish(msg.permission_denied())

    if len(args) != 2 or not args[0].isdigit() or args[1] not in ("禁止", "解禁"):
        await ban_user_bot.finish(msg.syntax_error())

    target = int(args[0])
    ban = args[1] == "禁止"
    db_user = await _get_or_create_user(target, session)
    db_user.allow_use_bot = not ban
    await DbUserRepo(session).update(db_user)

    target_name = await get_username(target, bot)
    if ban:
        await ban_user_bot.finish(msg.success(f"🚫已禁止{target_name} ({target})使用Bot"))
    else:
        await ban_user_bot.finish(msg.success(f"✅已解禁{target_name} ({target})使用Bot"))


ban_group_bot = on_command("禁止群", force_whitespace=True)


@ban_group_bot.handle()
async def _(bot: Bot, args: Args, session: Session, user: User, permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="禁止群",
        failed_msg="操作失败！",
        syntax="禁止群 <群号> <禁止|解禁>"
    )

    if not permission:
        await ban_group_bot.finish(msg.permission_denied())

    if len(args) != 2 or not args[0].isdigit() or args[1] not in ("禁止", "解禁"):
        await ban_group_bot.finish(msg.syntax_error())

    target = int(args[0])
    ban = args[1] == "禁止"
    db_group = await _get_or_create_group(target, session)
    db_group.allow_use_bot = not ban
    await DbGroupRepo(session).update(db_group)

    group_name = await get_group_name(target, bot)
    if ban:
        await ban_group_bot.finish(msg.success(f"🚫已禁止群{group_name} ({target})使用Bot"))
    else:
        await ban_group_bot.finish(msg.success(f"✅已解禁群{group_name} ({target})使用Bot"))


yun_hei_ban = on_command("云黑封禁", force_whitespace=True)


@yun_hei_ban.handle()
async def _(bot: Bot, args: Args, session: Session, user: User, permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="云黑封禁",
        failed_msg="操作失败！",
        syntax="云黑封禁 <QQ> <禁止|解禁>"
    )

    if not permission:
        await yun_hei_ban.finish(msg.permission_denied())

    if len(args) != 2 or not args[0].isdigit() or args[1] not in ("禁止", "解禁"):
        await yun_hei_ban.finish(msg.syntax_error())

    target = int(args[0])
    ban = args[1] == "禁止"
    db_user = await _get_or_create_user(target, session)
    db_user.allow_ban = not ban
    await DbUserRepo(session).update(db_user)

    target_name = await get_username(target, bot)
    if ban:
        await yun_hei_ban.finish(
            msg.success(f"🚫已禁止{target_name} ({target})提交云黑\n"
                        f"申诉请加反馈群: {config.bot_admin_group_id}")
        )
    else:
        await yun_hei_ban.finish(msg.success(f"✅已解禁{target_name} ({target})提交云黑"))


group_yun_hei_ban = on_command("群云黑封禁", force_whitespace=True)


@group_yun_hei_ban.handle()
async def _(bot: Bot, args: Args, session: Session, user: User, permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="群云黑封禁",
        failed_msg="操作失败！",
        syntax="群云黑封禁 <群号> <禁止|解禁>"
    )

    if not permission:
        await group_yun_hei_ban.finish(msg.permission_denied())

    if len(args) != 2 or not args[0].isdigit() or args[1] not in ("禁止", "解禁"):
        await group_yun_hei_ban.finish(msg.syntax_error())

    target = int(args[0])
    ban = args[1] == "禁止"
    db_group = await _get_or_create_group(target, session)
    db_group.allow_ban = not ban
    await DbGroupRepo(session).update(db_group)

    group_name = await get_group_name(target, bot)
    if ban:
        await group_yun_hei_ban.finish(
            msg.success(f"🚫已禁止群{group_name} ({target})提交云黑\n"
                        f"申诉请加反馈群: {config.bot_admin_group_id}")
        )
    else:
        await group_yun_hei_ban.finish(
            msg.success(f"✅已解禁群{group_name} ({target})提交云黑")
        )
