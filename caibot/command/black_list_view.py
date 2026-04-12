from nonebot import on_command
from nonebot.adapters.milky import Bot

from caibot import CommandMsg
from caibot.db import BanRecordRepo
from caibot.dependency import Args, Session, Group, User, CommonPermission, BotAdminPermission
from caibot.utils import get_username, get_group_name, ban_record_to_str, ban_record_to_detail


class BanUser:
    def __init__(self, user_id: int, name: str, ban_count: int):
        self.user_id = user_id
        self.username = name
        self.ban_count = ban_count

    def __str__(self):
        return f'#⃣[{self.username}] ({self.user_id}) - {self.ban_count}条'

PAGE_SIZE = 10

ban_list = on_command("云黑列表", force_whitespace=True)


@ban_list.handle()
async def _(bot: Bot, args: Args, session: Session, user: User, permission: CommonPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="云黑列表",
        syntax="云黑列表 [页码]"
    )

    if not permission:
        await ban_list.finish(msg.permission_denied())

    page = 1
    if len(args) == 1 and args[0].isdigit() and int(args[0]) >= 1:
        page = int(args[0])
    elif len(args) >= 1:
        await ban_list.finish(msg.syntax_error())

    ban_record_repo = BanRecordRepo(session)
    ban_records = await ban_record_repo.get_all()

    if not ban_records:
        await ban_list.finish(msg.success("✅云黑名单为空"))

    ban_count_map: dict[int, int] = {}
    for record in ban_records:
        ban_count_map[record.user_id] = ban_count_map.get(record.user_id, 0) + 1

    sorted_users = sorted(ban_count_map.items(), key=lambda x: x[1], reverse=True)
    total_users = len(sorted_users)
    total_pages = (total_users + PAGE_SIZE - 1) // PAGE_SIZE

    if page > total_pages:
        await ban_list.finish(msg.failed(f"页码超出范围，共 {total_pages} 页"))

    start = (page - 1) * PAGE_SIZE
    page_users = sorted_users[start:start + PAGE_SIZE]

    ban_users: list[BanUser] = []
    for uid, count in page_users:
        username = await get_username(uid, bot)
        ban_users.append(BanUser(uid, username, count))

    msg.sub_title = f"{page}/{total_pages}页"
    result_lines: list[str] = []
    for bu in ban_users:
        result_lines.append(str(bu))

    await ban_list.finish(msg.success("\n".join(result_lines)))


ban_detail = on_command("云黑详细", force_whitespace=True)


@ban_detail.handle()
async def _(args: Args, session: Session, user: User, permission: CommonPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="云黑详细",
        syntax="云黑详细 <记录ID>"
    )

    if not permission:
        await ban_detail.finish(msg.permission_denied())

    if len(args) != 1 or not args[0].isdigit():
        await ban_detail.finish(msg.syntax_error())

    record_id = int(args[0])
    ban_record_repo = BanRecordRepo(session)
    record = await ban_record_repo.get_by_id(record_id)

    if record is None:
        await ban_detail.finish(msg.failed(f"未找到记录#{record_id}"))

    assert record is not None
    detail = await ban_record_to_detail(record)
    await ban_detail.finish(msg.success(detail))


group_ban_list = on_command("群云黑列表", force_whitespace=True)


@group_ban_list.handle()
async def _(bot: Bot, args: Args, session: Session, user: User, permission: BotAdminPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="群云黑列表",
        syntax="群云黑列表 <群ID> [页码]"
    )

    if not permission:
        await group_ban_list.finish(msg.permission_denied())

    if len(args) == 0 or not args[0].isdigit():
        await group_ban_list.finish(msg.syntax_error())

    target_group_id = int(args[0])
    page = 1
    if len(args) == 2 and args[1].isdigit() and int(args[1]) >= 1:
        page = int(args[1])
    elif len(args) >= 2:
        await group_ban_list.finish(msg.syntax_error())

    ban_record_repo = BanRecordRepo(session)
    ban_records = await ban_record_repo.get_by_group_id(target_group_id)

    if not ban_records:
        await group_ban_list.finish(msg.success(f"✅该群云黑名单为空"))

    total = len(ban_records)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

    if page > total_pages:
        await group_ban_list.finish(msg.failed(f"页码超出范围，共 {total_pages} 页"))

    start = (page - 1) * PAGE_SIZE
    page_records = ban_records[start:start + PAGE_SIZE]

    result_lines: list[str] = []
    for record in page_records:
        username = await get_username(record.user_id, bot)
        result_lines.append(f"#⃣[{record.id}] {username} ({record.user_id}): {record.reason}")

    group_name = await get_group_name(target_group_id, bot)
    msg._sub_title = f"{page}/{total_pages}页"
    await group_ban_list.finish(
        msg.success(f"⚠️{group_name}共{total}条云黑记录:\n" + "\n".join(result_lines))
    )


ban_check = on_command("云黑检测", force_whitespace=True)


@ban_check.handle()
async def _(bot: Bot, args: Args, session: Session, group: Group, user: User, permission: CommonPermission):
    msg = CommandMsg(
        user_id=user.user_id,
        title="云黑检测",
        syntax="云黑检测 <QQ/all>"
    )

    if not permission:
        await ban_check.finish(
            msg.permission_denied()
        )

    if len(args) != 1 or (args[0] not in ['*', 'all'] and not args[0].isdigit()):
        await ban_check.finish(
            msg.syntax_error()
        )


    ban_record_repo = BanRecordRepo(session)

    if args[0] in ['*', 'all']:
        ban_records = await ban_record_repo.get_all()

        members = await bot.get_group_member_list(group_id=group.group_id)

        ban_count_map: dict[int, int] = {}
        for record in ban_records:
            ban_count_map[record.user_id] = ban_count_map.get(record.user_id, 0) + 1

        member_ids = {m.user_id for m in members}

        hit_user_ids = member_ids & ban_count_map.keys()

        if not hit_user_ids:
            await ban_check.finish(
                msg.success("✅本群没有成员在云黑名单中")
            )

        ban_users: list[BanUser] = []
        for uid in hit_user_ids:
            username = await get_username(uid, bot)
            ban_users.append(BanUser(uid, username, ban_count_map[uid]))

        ban_users.sort(key=lambda u: u.ban_count, reverse=True)

        result_lines = [f"⚠️本群共有{len(ban_users)}名成员在云黑名单中:"]
        for bu in ban_users:
            result_lines.append(str(bu))

        await ban_check.finish(
            msg.success("\n".join(result_lines))
        )

    else:
        target_id = int(args[0])
        ban_records = await ban_record_repo.get_by_user_id(target_id)
        target_username = await get_username(target_id, bot)

        if not ban_records:
            await ban_check.finish(
                msg.success(f"✅{target_username} ({target_id})不在云黑名单中")
            )

        result_lines: list[str] = []
        for record in ban_records:
            ban_msg = await ban_record_to_str(record)
            result_lines.append(ban_msg)

        await ban_check.finish(
            msg.success(f"⚠️{target_username}共有{len(ban_records)}条云黑记录:\n"+
                        "\n".join(result_lines))
        )

