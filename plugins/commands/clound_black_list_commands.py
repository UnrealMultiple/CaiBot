import random

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment

from common.ban_request import BanRequest
from common.ban_user import UserBan
from common.global_const import FEEDBACK_GROUP, TSHOCK_GROUP
from common.group import Group
from common.group_helper import GroupHelper


def msg_cut(msg: str) -> list:
    msg = msg.split(" ")
    msg = [word for word in msg if word]
    return msg


def paginate(data, page_size, page_number):
    # 计算开始和结束的索引
    start = (page_number - 1) * page_size
    end = start + page_size
    # 返回分页后的数据
    return data[start:end]


pending_list = on_command("审核列表", force_whitespace=True)
@pending_list.handle()
async def pending_list_handle(event: GroupMessageEvent):
    if await GroupHelper.is_superadmin(event.user_id):
        ban_requests = BanRequest.get_all()
        if len(ban_requests) == 0:
            await pending_list.finish(MessageSegment.at(event.user_id) +
                                      f'\n『云黑审核』\n' +
                                      "当前没有待审核的云黑捏~")
        await pending_list.finish(MessageSegment.at(event.user_id) +
                             f'\n『云黑审核』\n' +
                             '\n'.join([await i.to_oneline_string() for i in ban_requests]))

approve = on_command("批准云黑", force_whitespace=True, aliases= {"云黑批准"})
@approve.handle()
async def approve_handle(event: GroupMessageEvent):
    msg = msg_cut(GroupHelper.replace_at(event.raw_message))
    if await GroupHelper.is_superadmin(event.user_id):
        if len(msg) != 2:
            await approve.finish(MessageSegment.at(event.user_id) +
                                 f'\n『云黑审核』\n' +
                                 f"格式错误!正确格式: 批准云黑 <请求ID>")
        if not msg[1].isdigit():
            await approve.finish(MessageSegment.at(event.user_id) +
                                 f'\n『云黑审核』\n' +
                                 f"请求ID格式错误!")

        ban_request = BanRequest.get_by_id(msg[1])
        if ban_request is not None and not ban_request.handled:
            ban = UserBan.get_user(ban_request.target)
            if ban is None:
                ban = UserBan.add_user(ban_request.target)
            ban.add_ban(ban_request.group, ban_request.admin, ban_request.reason)
            ban_request.handled = True
            ban_request.update()
            await GroupHelper.send_group(ban_request.group, MessageSegment.at(ban_request.admin) +
                                      f'\n『云黑审核·{ban_request.target}』\n' +
                                      f'云黑请求#{ban_request.id}已被批准!')
            await approve.finish(MessageSegment.at(event.user_id) +
                                      f'\n『云黑审核』\n' +
                                      f'已批准#{ban_request.id}!')
        else:
            await approve.finish(MessageSegment.at(event.user_id) +
                                      f'\n『云黑审核』\n' +
                                      '无效的请求ID')

deny = on_command("驳回云黑", force_whitespace=True, aliases= {"云黑驳回"})
@deny.handle()
async def deny_handle(event: GroupMessageEvent):
    msg = msg_cut(GroupHelper.replace_at(event.raw_message))
    if await GroupHelper.is_superadmin(event.user_id):
        if len(msg) != 3:
            await approve.finish(MessageSegment.at(event.user_id) +
                                 f'\n『云黑审核』\n' +
                                 f"格式错误!正确格式: 驳回云黑 <请求ID> <原因>")
        if not msg[1].isdigit():
            await approve.finish(MessageSegment.at(event.user_id) +
                                 f'\n『云黑审核』\n' +
                                 f"请求ID格式错误!")

        ban_request = BanRequest.get_by_id(msg[1])
        if ban_request is not None and not ban_request.handled:
            ban_request.handled = True
            ban_request.update()
            await GroupHelper.send_group(ban_request.group, MessageSegment.at(ban_request.admin) +
                                         f'\n『云黑审核·{ban_request.target}』\n' +
                                         f'云黑请求#{ban_request.id}已被驳回!\n'+
                                         f'原因: {msg[2]}')
            await approve.finish(MessageSegment.at(event.user_id) +
                                 f'\n『云黑审核』\n' +
                                 f'已驳回#{ban_request.id}!')
        else:
            await approve.finish(MessageSegment.at(event.user_id) +
                                 f'\n『云黑审核』\n' +
                                 '无效的请求ID')


check_details = on_command("云黑详细", force_whitespace=True)


@check_details.handle()
async def check_details_handle(event: GroupMessageEvent):
    msg = msg_cut(GroupHelper.replace_at(event.raw_message))
    if await GroupHelper.HasPermission(event.group_id, event.user_id):

        group = Group.get_group(event.group_id)
        if group is None:
            await check_details.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑详细』\n'
                                       + "请启用云黑!\n"
                                         "发送'启用云黑'在本群启用本BOT")
        if len(msg) != 2:
            await check_details.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑详细』\n' +
                                       f"格式错误!正确格式: 云黑详细 <QQ号>")
        if not msg[1].isdigit():
            await check_details.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑详细』\n'
                                       + f"QQ号格式错误!")
        ban = UserBan.get_user(int(msg[1]))
        if ban is not None:
            if len(ban.bans) != 0:
                await check_details.finish(MessageSegment.at(event.user_id) +
                                           f'\n『云黑详细』\n' +
                                           f'⚠️检测到云黑记录({int(msg[1])})\n' +
                                           f'\n'.join([await x.to_details_string() for x in
                                                       ban.bans]))
            else:
                await check_details.finish(MessageSegment.at(event.user_id) +
                                           f'\n『云黑详细』\n' +
                                           "✅该账户不在云黑名单内")
        else:
            await check_details.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑详细』\n' +
                                       "✅该账户不在云黑名单内")
    else:
        await check_details.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑详细』\n' +
                                   "没有权限!\n"
                                   "云黑名单只允许群主和管理员使用")


check_ban = on_command("云黑检测", force_whitespace=True)


@check_ban.handle()
async def check_ban_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑检测』\n'
                               + "请启用云黑!\n"
                                 "发送'启用云黑'在本群启用本BOT")
    msg = msg_cut(GroupHelper.replace_at(event.raw_message))
    if len(msg) != 2:
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑检测』\n' +
                               f"格式错误!正确格式: 云黑检测 <QQ号>")
    if msg[1] == "*" or msg[1] == "all":
        result = await GroupHelper.check_ban_many(event.group_id)
        if len(result) == 0:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑检测』\n'
                                   + "本群没有人在云黑名单里哦!")
        else:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑检测』\n' +
                                   "⚠️检测到云黑记录:\n" +
                                   "\n".join(result))

        pass

    if not msg[1].isdigit():
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑检测』\n'
                               + f"QQ号格式错误!")
    ban = UserBan.get_user(int(msg[1]))
    if ban is not None:
        if len(ban.bans) != 0:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑检测』\n' +
                                   f'⚠️检测到云黑记录({int(msg[1])})\n' +
                                   f'\n'.join([await x.to_string() for x in
                                               ban.bans]))
        else:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑检测』\n'
                                   + "✅该账户不在云黑名单内")
    else:
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑检测』\n' +
                               "✅该账户不在云黑名单内")


del_ban = on_command("删除云黑", force_whitespace=True)


@del_ban.handle()
async def del_ban_handle(bot: Bot, event: GroupMessageEvent):
    msg = msg_cut(GroupHelper.replace_at(event.raw_message))
    group = Group.get_group(event.group_id)
    if group is None:
        await del_ban.finish(MessageSegment.at(event.user_id) +
                             f'\n『删除云黑』\n' +
                             "请启用云黑!\n"
                             "发送'启用云黑'在本群启用本BOT")
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 2:
            await del_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『删除云黑』\n' +
                                 f"格式错误!正确格式: 删除云黑 <QQ号> [只能删除本群添加的云黑]")
        if not msg[1].isdigit():
            await del_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『删除云黑』\n' +
                                 f"QQ号格式错误!")

        target = msg[1]

        ban = UserBan.get_user(target)
        if ban is not None:
            if ban.check_ban(event.group_id):
                ban.del_ban(event.group_id)
                await del_ban.send(MessageSegment.at(event.user_id) +
                                   f'\n『添加云黑』\n' +
                                   "云黑删除成功!")
                if event.group_id != FEEDBACK_GROUP:
                    await bot.send_group_msg(group_id=FEEDBACK_GROUP, message=
                    f'🗑️删除云黑 {await GroupHelper.GetName(target )} ({target})\n' +
                    f"剩余云黑数: {len(ban.bans)}\n" +
                    f"操作群: {await GroupHelper.GetGroupName(event.group_id)} ({event.group_id})")
            else:
                ban_request = BanRequest.get_by_target_and_group(target, event.group_id)
                if ban_request is not None:
                    ban_request.handled = True
                    ban_request.update()
                    if event.group_id != FEEDBACK_GROUP:
                        await bot.send_group_msg(group_id=FEEDBACK_GROUP, message=
                        f'🗑️撤销云黑请求#{ban_request.id} {await GroupHelper.GetName(target)} ({target})\n' +
                        f"管理员: {await GroupHelper.GetName(event.user_id)} ({event.user_id})\n"
                        f"操作群: {await GroupHelper.GetGroupName(event.group_id)} ({event.group_id})")

                    await del_ban.finish(MessageSegment.at(event.user_id) +
                                         f'\n『删除云黑』\n' +
                                         f"已撤销云黑申请#{ban_request.id}!")


                if len(ban.bans) == 0:
                    await del_ban.finish(MessageSegment.at(event.user_id) +
                                         f'\n『删除云黑』\n' +
                                         "该账户不在云黑名单内")
                else:
                    await del_ban.finish(MessageSegment.at(event.user_id) +
                                         f'\n『删除云黑』\n' +
                                         f"该账户不存在于本群云黑名单,无法删除!")
        else:
            await del_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『删除云黑』\n' +
                                 "该账户不在云黑名单内")

    else:
        await del_ban.finish(MessageSegment.at(event.user_id) +
                             f'\n『删除云黑』\n' +
                             "没有权限!\n"
                             "云黑名单只允许群主和管理员使用")


add_ban = on_command("添加云黑", force_whitespace=True)


@add_ban.handle()
async def add_ban_handle(bot: Bot, event: GroupMessageEvent):
    message_text = GroupHelper.replace_at(event.raw_message)
    msg = message_text.split(" ", 2)

    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        group = Group.get_group(event.group_id)
        if group is None:
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n' +
                                 "请启用云黑!\n"
                                 "发送'启用云黑'在本群启用本BOT")
        if len(msg) != 3:
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n'
                                 + f"格式错误!正确格式: 添加云黑 <QQ号> <理由> [乱写理由禁用添加功能]")
        if not msg[1].isdigit():
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n' +
                                 f"QQ号格式错误!")
        if msg[2].isdigit():
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n' +
                                 f"理由不可以是纯数字!")

        if group.reject_edition:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『添加云黑』\n'
                                   + "本群被开发者标记为禁止添加云黑!\n"
                                     "申诉请直接加Cai(3042538328)[仅周六]")
        target = int(msg[1])


        ban_request = BanRequest.get_by_target_and_group(target, event.group_id)
        if ban_request is not None:
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n' +
                                 f"你已经提交过本云黑申请!")

        ban = UserBan.get_user(target)

        if ban is not None:
            if ban.check_ban_user(event.user_id):
                await add_ban.finish(MessageSegment.at(event.user_id) +
                                     f'\n『添加云黑』\n' +
                                     f"你已经为本账户添加过云黑了!")
            if ban.check_ban(event.group_id):
                await add_ban.finish(MessageSegment.at(event.user_id) +
                                     f'\n『添加云黑』\n' +
                                     f"该账户已存在于本群云黑名单!")

        if await group.can_add() or event.group_id == FEEDBACK_GROUP:
            id = BanRequest.add(target,event.group_id,event.user_id,msg[2])
            group.add_ban(target)
            await add_ban.send(MessageSegment.at(event.user_id) +
                               f'\n『添加云黑』\n' +
                               f"已向反馈群提交申请#{id}!({target})")
            if event.group_id != FEEDBACK_GROUP:
                await bot.send_group_msg(group_id=FEEDBACK_GROUP, message=
                f'🙏云黑请求#{id} {await GroupHelper.GetName(target)} ({target})\n' +
                f"管理员: {await GroupHelper.GetName(event.user_id)} ({event.user_id})\n"
                f"添加群: {await GroupHelper.GetGroupName(event.group_id)} ({event.group_id})\n"
                f"理由: {msg[2]}")
        else:
            has_add = group.count_bans_in_last_day()
            max_add = await group.can_add_max()
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n' +
                                 f"❌本群目前规模只能每天添加{max_add}个云黑\n"
                                 f"今天已添加云黑{has_add}个")
    else:
        await add_ban.finish(MessageSegment.at(event.user_id) +
                             f'\n『添加云黑』\n' +
                             "没有权限!\n"
                             "云黑名单只允许群主和管理员使用")


ban_list = on_command("云黑列表", force_whitespace=True)


@ban_list.handle()
async def ban_list_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await ban_list.finish(MessageSegment.at(event.user_id) +
                              f'\n『云黑列表』\n'
                              + "请启用云黑!\n"
                                "发送'启用云黑'在本群启用本BOT")
    msg = msg_cut(event.get_plaintext())
    if len(msg) == 1:
        page_number = 1
    else:
        try:
            page_number = int(msg[1])
        except ValueError:
            page_number = 1
    result = UserBan.get_all_bans()
    # 首先，我们需要对结果进行排序
    result.sort(key=lambda x: len(x.bans), reverse=True)

    # 然后，我们可以生成我们的列表
    result = paginate(result, 10, page_number)
    bans = [f"#⃣{i.id}: {len(i.bans)}条云黑记录" for i in result]

    if len(result) == 0:
        await ban_list.finish(MessageSegment.at(event.user_id) +
                              f'\n『云黑列表』\n'
                              + "云黑系统没有检测到任何记录!")
    else:
        await ban_list.finish(MessageSegment.at(event.user_id) +
                              f'\n『云黑列表』\n' +
                              "⚠️检测到云黑记录:\n" +
                              "\n".join(bans) +
                              "\n翻页：云黑列表 <页码>")


random_ban = on_command("随机云黑", force_whitespace=True)


@random_ban.handle()
async def random_ban_handle(event: GroupMessageEvent):
    if event.group_id == TSHOCK_GROUP:
        return
    group = Group.get_group(event.group_id)
    if group is None:
        await random_ban.finish(MessageSegment.at(event.user_id) +
                                f'\n『随机云黑』\n'
                                + "请启用云黑!\n"
                                  "发送'启用云黑'在本群启用本BOT")

    result = UserBan.get_all_bans()
    ban = random.choice(result)

    await random_ban.finish(MessageSegment.at(event.user_id) +
                            f'\n『随机云黑』\n' +
                            f'⚠️检测到云黑记录({ban.id})\n' +
                            f'\n'.join([await x.to_string() for x in
                                        ban.bans]))


group_ban_list = on_command("群云黑列表", force_whitespace=True)


@group_ban_list.handle()
async def group_ban_list_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『随机云黑』\n'
                                    + "请启用云黑!\n"
                                      "发送'启用云黑'在本群启用本BOT")

    msg = msg_cut(event.get_plaintext())
    group_num = 0
    if len(msg) != 2:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑列表』\n'
                                    + "格式错误!正确格式: 群云黑列表 <QQ群号>")
    else:
        try:
            group_num = int(msg[1])
        except ValueError:
            await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                        f'\n『云黑列表』\n'
                                        + "格式错误!无效QQ群号")

    result = UserBan.get_all_bans()
    bans = []
    for i in result:
        for n in i.bans:
            if n.group == group_num:
                n.id = i.id
                bans.append(n)

    if len(bans) == 0:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑列表({group_num})』\n'
                                    + "🔍没有检测到任何记录!")
    else:

        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑列表({group_num})』\n' +
                                    "⚠️检测到云黑记录:\n" +
                                    f'\n'.join([await x.to_group_string() for x in
                                                bans]))


group_ban_clean = on_command("群云黑清空", force_whitespace=True)


@group_ban_clean.handle()
async def group_ban_clean_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await group_ban_clean.finish(MessageSegment.at(event.user_id) +
                                     f'\n『云黑删除』\n'
                                     + "请启用云黑!\n"
                                       "发送'启用云黑'在本群启用本BOT")
    if not await GroupHelper.is_superadmin(event.user_id):
        await group_ban_del.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑删除』\n'
                                   + "没有权限,此命令需要CaiBot管理成员才能执行!")
    msg = msg_cut(event.get_plaintext())
    group_num = 0
    if len(msg) != 2:
        await group_ban_clean.finish(MessageSegment.at(event.user_id) +
                                     f'\n『云黑删除』\n'
                                     + "格式错误!正确格式: 群云黑清空 <QQ群号>")
    else:
        try:
            group_num = int(msg[1])
        except ValueError:
            await group_ban_clean.finish(MessageSegment.at(event.user_id) +
                                         f'\n『云黑删除』\n'
                                         + "格式错误!无效QQ群号")

    result = UserBan.get_all_bans()
    bans = []
    for i in result:
        for n in i.bans:
            if n.group == group_num:
                n.id = i.id
                bans.append(n)
                i.del_ban(group_num)

    if len(bans) == 0:
        await group_ban_clean.finish(MessageSegment.at(event.user_id) +
                                     f'\n『云黑删除({group_num})』\n'
                                     + "检测到任何记录!")
    else:
        await group_ban_clean.finish(MessageSegment.at(event.user_id) +
                                     f'\n『云黑删除({group_num})』\n' +
                                     "✅已删除记录:\n" +
                                     f'\n'.join([await x.to_group_string() for x in
                                                 bans]))


group_ban_add = on_command("群云黑封禁", force_whitespace=True)


@group_ban_add.handle()
async def group_ban_list_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await group_ban_add.finish(MessageSegment.at(event.user_id) +
                                   f'\n『群云黑封禁』\n'
                                   + "请启用云黑!\n"
                                     "发送'启用云黑'在本群启用本BOT")
    if not await GroupHelper.is_superadmin(event.user_id):
        await group_ban_del.finish(MessageSegment.at(event.user_id) +
                                   f'\n『群云黑封禁』\n'
                                   + "没有权限,此命令需要CaiBot管理成员才能执行!")
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await group_ban_add.finish(MessageSegment.at(event.user_id) +
                                   f'\n『群云黑封禁』\n'
                                   + "格式错误!正确格式: 群云黑封禁 <QQ群号>")
    else:
        try:
            group_num = int(msg[1])
        except ValueError:
            await group_ban_add.finish(MessageSegment.at(event.user_id) +
                                       f'\n『群云黑封禁』\n'
                                       + "格式错误!无效QQ群号")

    target_group = Group.get_group(group_num)
    if group is None:
        await group_ban_add.finish(MessageSegment.at(event.user_id) +
                                   f'\n『群云黑封禁』\n'
                                   + "本群没有使用CaiBot捏\n")
    if target_group.reject_edition:
        target_group.reject_edition = False
        target_group.update()
        await group_ban_add.finish(MessageSegment.at(event.user_id) +
                                   f'\n『群云黑封禁({group_num})』\n'
                                   + "已解除添加云黑限制!")
    else:
        target_group.reject_edition = True
        target_group.update()
        await group_ban_add.finish(MessageSegment.at(event.user_id) +
                                   f'\n『群云黑封禁({group_num})』\n'
                                   + "已禁止其添加云黑!")


group_ban_del = on_command("群云黑删除", force_whitespace=True)


@group_ban_del.handle()
async def group_ban_list_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await group_ban_del.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑删除』\n'
                                   + "请启用云黑!\n"
                                     "发送'启用云黑'在本群启用本BOT")
    if not await GroupHelper.is_superadmin(event.user_id):
        await group_ban_del.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑删除』\n'
                                   + "没有权限,此命令需要CaiBot管理成员才能执行!")
    msg = msg_cut(event.get_plaintext())
    group = 0
    target = 0
    if len(msg) != 3:
        await group_ban_del.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑删除』\n'
                                   + "格式错误!正确格式: 群云黑删除 <QQ号> <QQ群号>")
    else:
        try:
            target = int(msg[1])
            group = int(msg[2])
        except ValueError:
            await group_ban_del.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑删除』\n'
                                       + "格式错误!无效QQ群号或QQ号")
    result = UserBan.get_all_bans()
    bans = []
    for i in result:
        for n in i.bans:
            if i.id == target and n.group == group:
                n.id = i.id
                bans.append(n)
                i.del_ban(group)

    if len(bans) == 0:
        await group_ban_del.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑删除({group}=>{target})』\n'
                                   + "检测到任何记录!")
    else:
        await group_ban_del.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑删除({group}=>{target})』\n' +
                                   "✅已删除记录:\n" +
                                   f'\n'.join([await x.to_group_string() for x in
                                               bans]))
