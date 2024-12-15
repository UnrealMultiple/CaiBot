from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

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

del_admin = on_command("云黑管理删除", aliases={"删除管理", "管理删除"}, force_whitespace=True)


@del_admin.handle()
async def add_admin_handle(event: GroupMessageEvent):
    msg = msg_cut(event.get_plaintext())
    if await GroupHelper.is_owner(event.group_id, event.user_id):

        group = Group.get_group(event.group_id)
        if group is None:
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『BOT管理』\n' +
                                   "请启用云黑!\n"
                                   "发送'启用云黑'在本群启用本BOT")
        else:
            if len(msg) != 2:
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『BOT管理』\n' +
                                       f"格式错误!正确格式: 删除管理 <QQ号> [只在本群有效]")
            if not msg[1].isdigit():
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『BOT管理』\n' +
                                       f"QQ号格式错误!")
            if int(msg[1]) in group.admins:
                group.admins.remove(int(msg[1]))
                group.update()
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『BOT管理』\n' +
                                       f"{int(msg[1])}不再是本群BOT管理!")

            else:
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『BOT管理』\n' +
                                       "该用户不是本群BOT管理!")
    else:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『BOT管理』\n' +
                               "没有权限!\n"
                               "只允许群主使用")


add_admin = on_command("云黑管理添加", aliases={"添加管理", "管理添加"}, force_whitespace=True)


@add_admin.handle()
async def add_admin_handle(event: GroupMessageEvent):
    msg = msg_cut(event.get_plaintext())
    if await GroupHelper.is_owner(event.group_id, event.user_id):

        group = Group.get_group(event.group_id)
        if group is None:
            await add_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『BOT管理』\n' +
                                   "请启用云黑!\n"
                                   "发送'启用云黑'在本群启用本BOT")
        else:
            if len(msg) != 2:
                await add_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『BOT管理』\n' +
                                       f"格式错误!正确格式: 添加管理 <QQ号> [只在本群有效]")
            if not msg[1].isdigit():
                await add_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『BOT管理』\n' +
                                       f"QQ号格式错误!")
            if int(msg[1]) in group.admins:
                await add_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『BOT管理』\n' +
                                       "该用户已是本群BOT管理!")
            else:
                group.admins.append(int(msg[1]))
                group.update()
                await add_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       f"已将{int(msg[1])}设为本群BOT管理!")
    else:
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑管理』\n' +
                               "没有权限!\n"
                               "只允许群主使用")


agreement = on_command("启用云黑", aliases={"加入云黑"}, force_whitespace=True)


@agreement.handle()
async def agreement_handle(event: GroupMessageEvent):
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        group = Group.get_group(event.group_id)
        if group is not None:
            await agreement.finish(MessageSegment.at(event.user_id) +
                                   f'\n『启用云黑』\n' +
                                   "本群已启用云黑名单,无需重复启用!")
        Group.add_group(event.group_id)
        await agreement.finish(MessageSegment.at(event.user_id) +
                               f'\n『启用云黑』\n' +
                               "✅本群已开启云黑名单!\n"
                               "⚠自动踢出功能在设为管理员后自动开启!\n"
                               "1.此云黑没有任何乱踢人的后门\n"
                               "2.此云黑永久免费\n"
                               "3.添加云黑请详细填写理由\n"
                               "4.云黑仅限泰拉瑞亚内行为(例如炸图、开挂等)\n"
                               "5.乱加云黑会被开发者封禁添加云黑功能\n"
                               "机器人模式教程: https://tr.monika.love/resources/118/")
    else:
        await agreement.finish(MessageSegment.at(event.user_id) +
                               f'\n『启用云黑』\n' +
                               "没有权限!\n"
                               "只允许群主和管理员设置")


agreement2 = on_command("启用群机器人", aliases={"启用机器人"}, force_whitespace=True)


@agreement2.handle()
async def agreement2_handle(event: GroupMessageEvent):
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        group = Group.get_group(event.group_id)
        if group is None:
            await agreement2.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群机器人』\n' +
                                    "请先启用云黑!")
        group.enable_server_bot = True
        group.update()
        await agreement2.finish(MessageSegment.at(event.user_id) +
                                f'\n『群机器人』\n' +
                                "✅本群已开启群机器人!\n"
                                "1.找到适配插件，下载并安装\n"
                                "2.重启服务器，用'添加服务器'来绑定服务器\n"
                                "3.如果你不需要白名单，可以在tshock/CaiBot.json关闭它\n"
                                "详细安装教程: https://tr.monika.love/resources/118/")
    else:
        await agreement2.finish(MessageSegment.at(event.user_id) +
                                f'\n『群机器人』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")


agreement3 = on_command("关闭群机器人", force_whitespace=True)


@agreement3.handle()
async def agreement3_handle(event: GroupMessageEvent):
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        group = Group.get_group(event.group_id)
        if group is None:
            await agreement3.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群机器人』\n' +
                                    "请先加入云黑!")
        group.enable_server_bot = False
        group.update()
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『群机器人』\n' +
                                "❌本群已关闭群机器人!")
    else:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『群机器人』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")


agreement4 = on_command('开启群管理员权限', force_whitespace=True)


@agreement4.handle()
async def agreement4_handle(event: GroupMessageEvent):
    if not await GroupHelper.is_owner(event.group_id, event.user_id):
        await agreement4.finish(MessageSegment.at(event.user_id) + '\n『群机器人』\n' + '只允许群主设置')
    group = Group.get_group(event.group_id)
    if group is None:
        await agreement4.finish(MessageSegment.at(event.user_id) + '\n『群机器人』\n' + '无法获取群信息')
    has_perm = group.config.get('group_admin_has_permission')
    if has_perm:
        await agreement4.finish(MessageSegment.at(event.user_id) + '\n『群机器人』\n' + '群管理员权限已开启')
    else:
        group.config['group_admin_has_permission'] = True
        group.update()
        await agreement4.finish(MessageSegment.at(event.user_id) + '\n『群机器人』\n' + '群管理员权限启用成功')


agreement5 = on_command('关闭群管理员权限', force_whitespace=True)


@agreement5.handle()
async def agreement5_handle(event: GroupMessageEvent):
    if not await GroupHelper.is_owner(event.group_id, event.user_id):
        await agreement5.finish(MessageSegment.at(event.user_id) + '\n『群机器人』\n' + '只允许群主设置')
    group = Group.get_group(event.group_id)
    if group is None:
        await agreement5.finish(MessageSegment.at(event.user_id) + '\n『群机器人』\n' + '无法获取群信息')
    has_perm = group.config.get('group_admin_has_permission')
    if has_perm:
        group.config['group_admin_has_permission'] = False
        group.update()
        await agreement5.finish(MessageSegment.at(event.user_id) + '\n『群机器人』\n' + '群管理员权限关闭成功')
    else:
        await agreement5.finish(MessageSegment.at(event.user_id) + '\n『群机器人』\n' + '群管理员权限未启用')
