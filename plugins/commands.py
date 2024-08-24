import datetime
import random
import re
import socket
import uuid
from urllib import parse

import aiohttp
import requests
from nonebot import on_command, on_startswith
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment

from plugins import API
from plugins.API import send_data, wait_for_online, server_available, disconnect, get_server
from utils.ban_user import UserBan
from utils.group import Group
from utils.group_helper import GroupHelper
from utils.server import Server
from utils.server_helper import set_server, ping_server
from utils.statistics import Statistics
from utils.text_handle import TextHandle
from utils.user import User, LoginRequest

FEED_BACK_GROUP = 991556763


async def get_hitokoto() -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://oiapi.net/API/AWord", ssl=False) as response:
                data = await response.json()
                sentence = (f"{data['message']}\n"
                            f"—— {data['data']['from']}")
                return sentence
    except Exception as ex:
        print(ex)
        return "Oiapi.net错误!"


def paginate(data, page_size, page_number):
    # 计算开始和结束的索引
    start = (page_number - 1) * page_size
    end = start + page_size
    # 返回分页后的数据
    return data[start:end]


del_admin = on_command("云黑管理删除", aliases={"删除管理", "管理删除"})


@del_admin.handle()
async def add_admin_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ", 1)
    if await GroupHelper.is_owner(event.group_id, event.user_id):

        group = Group.get_group(event.group_id)
        if group is None:
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑管理』\n' +
                                   "请启用云黑!\n"
                                   "发送'启用云黑'在本群启用本BOT")
            return
        else:
            if len(msg) != 2:
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       f"格式错误!正确格式: 云黑管理删除 <QQ号> [只在本群有效]")
                return
            if not msg[1].isdigit():
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       f"QQ号格式错误!")
                return
            if int(msg[1]) in group.admins:
                group.admins.remove(int(msg[1]))
                group.update()
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       f"{int(msg[1])}不再是本群云黑管理!")

            else:
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       "该用户不是本群云黑管理!")
    else:
        await del_ban.finish(MessageSegment.at(event.user_id) +
                             f'\n『云黑管理』\n' +
                             "没有权限!\n"
                             "只允许群主使用")


add_admin = on_command("云黑管理添加", aliases={"添加管理", "管理添加"})


@add_admin.handle()
async def add_admin_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ", 1)
    if await GroupHelper.is_owner(event.group_id, event.user_id):

        group = Group.get_group(event.group_id)
        if group is None:
            await add_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑管理』\n' +
                                   "请启用云黑!\n"
                                   "发送'启用云黑'在本群启用本BOT")
            return
        else:
            if len(msg) != 2:
                await add_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       f"格式错误!正确格式: 云黑管理添加 <QQ号> [只在本群有效]")
                return
            if not msg[1].isdigit():
                await add_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       f"QQ号格式错误!")
                return
            if int(msg[1]) in group.admins:
                await add_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       "该用户已是本群云黑管理!")
            else:
                group.admins.append(int(msg[1]))
                group.update()
                await add_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑管理』\n' +
                                       f"已将{int(msg[1])}设为本群云黑管理!")
    else:
        await del_ban.finish(MessageSegment.at(event.user_id) +
                             f'\n『云黑管理』\n' +
                             "没有权限!\n"
                             "只允许群主使用")


ban_help = on_command("云黑帮助", aliases={"帮助"})


@ban_help.handle()
async def ban_help_handle(bot: Bot, event: GroupMessageEvent):
    await ban_help.finish(MessageSegment.at(event.user_id) +
                          f'\n『云黑帮助』\n'
                          f'⚡添加云黑 <QQ号> <理由> [乱写理由禁用添加功能]\n'
                          f'⚡删除云黑 <QQ号> [只能删除本群添加的云黑]\n'
                          f'⚡云黑检测 <QQ号> [all/*表示全群检测]\n'
                          f'⚡云黑详细 <QQ号> [包含群号、添加者]\n'
                          f'⚡云黑管理添加 <QQ号> [添加云黑管理]\n'
                          f'⚡云黑管理删除 <QQ号> [删除云黑管理]\n'
                          f'⚡群云黑列表 <群号> [查看这个群加的云黑]\n'
                          f'⚡群云黑清空 <群号> [删除这个群加的所以云黑]\n'
                          f'⚡群云黑删除 <QQ号> <群号> [删除一条该群加的云黑]\n'
                          f'⚡群云黑封禁 <群号> [禁止一个群添加云黑]\n'
                          f'⚡云黑列表 <页码> [查看小黑屋]\n'
                          f'⚡随机云黑 [随机查看一个云黑]\n'
                          f'⚡关于 [查看CaiBot的奇奇怪怪东西]\n'
                          f'⚡启用群机器人 [启用群机器人功能]\n'
                          f'🔋设为管理员后可自动拒绝云黑加群\n'
                          f'🔋在被两个群以上标记为云黑会被加入真云黑\n'
                          f'🔋每天可加云黑人数视群人数而定')


ban_about = on_command("关于")


@ban_about.handle()
async def ban_about_handle(bot: Bot, event: GroupMessageEvent):
    statistics = Statistics.get_statistics()
    await ban_about.finish(MessageSegment.at(event.user_id) +
                           f'\n『关于』\n'
                           f'📖小小Cai\n'
                           f'🎉开发者: Cai(3042538328)\n'
                           f'🎉特别鸣谢: \n'
                           f'迅猛龙(3407905827) [提供服务器]\n'
                           f'羽学(1242509682) [代码贡献]\n'
                           f'🌐反馈群: 991556763\n'
                           f'⚡小小Cai已加入{statistics.total_group}个群,已记录{statistics.total_ban}名云黑用户\n'
                           f'入群检测{statistics.total_check}次,拒绝了{statistics.total_kick}次入群请求\n'
                           f'绑定{statistics.total_users}名玩家,检查白名单{statistics.check_whitelist}次\n'
                           f'绑定{statistics.total_servers}台服务器,当前已连接{len(API.websocket_connections)}台\n'
                           f'Powered by Nonebot2 & LLOneBot')


check_details = on_command("云黑详细")


@check_details.handle()
async def check_details_handle(bot: Bot, event: GroupMessageEvent):
    message_text = GroupHelper.replace_at(event.raw_message)
    msg = message_text.split(" ", 1)
    if await GroupHelper.HasPermission(event.group_id, event.user_id):

        group = Group.get_group(event.group_id)
        if group is None:
            await check_details.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑详细』\n'
                                       + "请启用云黑!\n"
                                         "发送'启用云黑'在本群启用本BOT")
            return
        if len(msg) != 2:
            await check_details.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑详细』\n' +
                                       f"格式错误!正确格式: 云黑详细 <QQ号>")
            return
        if not msg[1].isdigit():
            await check_details.finish(MessageSegment.at(event.user_id) +
                                       f'\n『云黑详细』\n'
                                       + f"QQ号格式错误!")
            return
        ban = UserBan.get_user(int(msg[1]))
        if ban is not None:
            if len(ban.bans) != 0:
                await check_details.finish(MessageSegment.at(event.user_id) +
                                           f'\n『云黑详细』\n' +
                                           f'⚠检测到云黑记录({int(msg[1])})\n' +
                                           f'\n'.join([await x.to_details_string() for x in
                                                       ban.bans]))
                return
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


check_ban = on_command("云黑检测")


@check_ban.handle()
async def check_ban_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑检测』\n'
                               + "请启用云黑!\n"
                                 "发送'启用云黑'在本群启用本BOT")
        return
    message_text = GroupHelper.replace_at(event.raw_message)
    msg = message_text.split(" ", 1)
    if len(msg) != 2:
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑检测』\n' +
                               f"格式错误!正确格式: 云黑检测 <QQ号>")
        return
    if msg[1] == "*" or msg[1] == "all":
        result = await GroupHelper.check_ban_many(event.group_id)
        if len(result) == 0:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑检测』\n'
                                   + "本群没有人在云黑名单里哦!")
        else:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑检测』\n' +
                                   "⚠检测到云黑记录:\n" +
                                   "\n".join(result))

        pass
        return

    if not msg[1].isdigit():
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑检测』\n'
                               + f"QQ号格式错误!")
        return
    ban = UserBan.get_user(int(msg[1]))
    if ban is not None:
        if len(ban.bans) != 0:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑检测』\n' +
                                   f'⚠检测到云黑记录({int(msg[1])})\n' +
                                   f'\n'.join([await x.to_string() for x in
                                               ban.bans]))
            return
        else:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『云黑检测』\n'
                                   + "✅该账户不在云黑名单内")
    else:
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『云黑检测』\n' +
                               "✅该账户不在云黑名单内")


del_ban = on_command("删除云黑")


@del_ban.handle()
async def del_ban_handle(bot: Bot, event: GroupMessageEvent):
    message_text = GroupHelper.replace_at(event.raw_message)
    msg = message_text.split(" ", 1)
    group = Group.get_group(event.group_id)
    if group is None:
        await del_ban.finish(MessageSegment.at(event.user_id) +
                             f'\n『删除云黑』\n' +
                             "请启用云黑!\n"
                             "发送'启用云黑'在本群启用本BOT")
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 2:
            await del_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『删除云黑』\n' +
                                 f"格式错误!正确格式: 删除云黑 <QQ号> [只能删除本群添加的云黑]")
            return
        if not msg[1].isdigit():
            await del_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『删除云黑』\n' +
                                 f"QQ号格式错误!")
            return

        ban = UserBan.get_user(int(msg[1]))
        if ban is not None:
            if ban.check_ban(event.group_id):
                ban.del_ban(event.group_id)
                await del_ban.send(MessageSegment.at(event.user_id) +
                                   f'\n『添加云黑』\n' +
                                   "云黑删除成功!")
                await bot.send_group_msg(group_id=FEED_BACK_GROUP, message=
                f'🔄️删除云黑 {await GroupHelper.GetName(int(msg[1]))} ({int(msg[1])})\n' +
                f"剩余云黑数: {len(ban.bans)}\n" +
                f"操作群: {await GroupHelper.GetGroupName(event.group_id)} ({event.group_id})")
            else:
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


add_ban = on_command("添加云黑")


@add_ban.handle()
async def add_ban_handle(bot: Bot, event: GroupMessageEvent):
    message_text = GroupHelper.replace_at(event.raw_message)
    msg = message_text.split(" ", 2)
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        group = Group.get_group(event.group_id)
        if group is None:
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n' +
                                 "请启用云黑!\n发送'启用云黑'在本群启用本BOT")
            return
        if len(msg) != 3:
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n'
                                 + f"格式错误!正确格式: 添加云黑 <QQ号> <理由> [乱写理由禁用添加功能]")
            return
        if not msg[1].isdigit():
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n' +
                                 f"QQ号格式错误!")
            return
        if msg[2].isdigit():
            await add_ban.finish(MessageSegment.at(event.user_id) +
                                 f'\n『添加云黑』\n' +
                                 f"理由不可以是纯数字!")
            return

        if group.reject_edition:
            await check_ban.finish(MessageSegment.at(event.user_id) +
                                   f'\n『添加云黑』\n'
                                   + "本群被开发者标记为禁止添加云黑!\n"
                                     "申诉请直接加Cai(3042538328)[仅周六]")
        ban = UserBan.get_user(int(msg[1]))

        if ban is not None:
            if ban.check_ban_user(event.user_id):
                await add_ban.finish(MessageSegment.at(event.user_id) +
                                     f'\n『添加云黑』\n' +
                                     f"你已经为本账户添加过云黑了!")
            if ban.check_ban(event.group_id):
                await add_ban.finish(MessageSegment.at(event.user_id) +
                                     f'\n『添加云黑』\n' +
                                     f"该账户已存在于本群云黑名单!")
        else:
            ban = UserBan.add_user(int(msg[1]))

        if await group.can_add():
            ban.add_ban(event.group_id, event.user_id, msg[2])
            group.add_ban(int(msg[1]))
            await add_ban.send(MessageSegment.at(event.user_id) +
                               f'\n『添加云黑』\n' +
                               f"云黑已添加!({int(msg[1])})")
            await bot.send_group_msg(group_id=FEED_BACK_GROUP, message=
            f'⬇️新云黑 {await GroupHelper.GetName(int(msg[1]))} ({int(msg[1])})\n' +
            f"理由: {msg[2]}\n"
            f"添加群: {await GroupHelper.GetGroupName(event.group_id)} ({event.group_id})")
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


agreement = on_command("启用云黑")


@agreement.handle()
async def agreement_handle(bot: Bot, event: GroupMessageEvent):
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        group = Group.get_group(event.group_id)
        if group is not None:
            await agreement.finish(MessageSegment.at(event.user_id) +
                                   f'\n『启用云黑』\n' +
                                   "本群已加入云黑名单!")
            return
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


agreement2 = on_command("启用群机器人", aliases={"启用机器人"})


@agreement2.handle()
async def agreement2_handle(bot: Bot, event: GroupMessageEvent):
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        group = Group.get_group(event.group_id)
        if group is None:
            await agreement2.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群机器人』\n' +
                                    "请先加入云黑!")
            return
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


agreement3 = on_command("关闭群机器人")


@agreement3.handle()
async def agreement3_handle(bot: Bot, event: GroupMessageEvent):
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        group = Group.get_group(event.group_id)
        if group is None:
            await agreement3.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群机器人』\n' +
                                    "请先加入云黑!")
            return
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


add_server = on_command("添加服务器")


@add_server.handle()
async def add_server_handle(bot: Bot, event: GroupMessageEvent):
    if not await GroupHelper.HasPermission(event.group_id, event.user_id):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『添加服务器』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")
        return
    group = Group.get_group(event.group_id)
    if group is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『添加服务器』\n' +
                                "请先加入云黑!\n" +
                                "群内发送'启用云黑'")
        return
    if not group.enable_server_bot:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『添加服务器』\n' +
                                "请启用群机器人!" +
                                "群内发送'启用群机器人'")
    msg = event.get_plaintext().split(" ")
    if len(msg) != 4:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『添加服务器』\n' +
                               f"格式错误!正确格式: 添加服务器 <IP地址> <端口> <验证码> [需要服务器适配插件]")
    try:
        res = await set_server(msg[1], int(msg[2]), int(msg[3]))
    except:
        API.add_token(int(msg[3]), Server(str(uuid.uuid4()), event.group_id, [], msg[1], int(msg[2])), 300)
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『添加服务器』\n' +
                               f"服务器连接失败,请检查地址、端口是否正确\n"
                               f"正在尝试被动连接! (请确保你的绑定码正确)")
        return
    if res is None:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『添加服务器』\n' +
                               f"目标服务器没有添加机器人适配插件")
    elif res == 'exist':
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『添加服务器』\n' +
                               f"绑定失败！\n此服务器已被绑定！")
    elif res == 'code':
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『添加服务器』\n' +
                               f"验证码错误！")
    else:
        pattern = r'^\{?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}?$'
        match = re.match(pattern, res)
        if not bool(match):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『添加服务器』\n' +
                                   f"绑定失败！\n服务器绑定无效，请重试！")
            return
        # group.servers.append(Server(res, event.group_id, [], msg[1], int(msg[2])))
        Server.add_server(res, event.group_id, msg[1], int(msg[2]))
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『添加服务器』\n' +
                               f"服务器绑定成功")


share_server = on_command("共享服务器")


@share_server.handle()
async def share_server_handle(bot: Bot, event: GroupMessageEvent):
    if not await GroupHelper.HasPermission(event.group_id, event.user_id):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『共享服务器』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")
    group = Group.get_group(event.group_id)
    if group is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『共享服务器』\n' +
                                "请先加入云黑!\n" +
                                "群内发送'启用云黑'")
        return
    if not group.enable_server_bot:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『共享服务器』\n' +
                                "请启用群机器人!" +
                                "群内发送'启用群机器人'")
    msg = event.get_plaintext().split(" ")
    if len(msg) != 3:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n' +
                               f"格式错误!正确格式: 共享服务器 <服务器序号> <共享服务器群号>")
        return
    if not msg[2].isdigit():
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               + f"QQ群号格式错误!")
        return
    if int(msg[2]) == event.group_id:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               f'Cai向Cai分享了Cai的Cai服务器\n'
                               f'这合理吗?')
    if not await GroupHelper.is_admin(int(msg[2]), event.user_id):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               f'没有权限哦~\n'
                               f"你必须是群[{msg[2]}]的管理员或群主!")
        return
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               f"服务器序号错误!")
        return
    if not group.servers[int(msg[1]) - 1].is_owner_server(event.group_id):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               f"只能由服务器拥有群[{group.servers[int(msg[1]) - 1].owner}]发起共享!")
        return
    if int(msg[2]) in group.servers[int(msg[1]) - 1].shared:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               f"本群已被共享过此服务器!")
        return
    group.servers[int(msg[1]) - 1].shared.append(int(msg[2]))
    group.servers[int(msg[1]) - 1].update()
    await disconnect(group.servers[int(msg[1]) - 1].token)
    await del_admin.finish(MessageSegment.at(event.user_id) +
                           f'\n『共享服务器』\n'
                           f"共享成功!\n"
                           f"你可以使用'取消共享服务器'来取消对目标群的服务器共享哦~")


unshare_server = on_command("取消共享服务器")


@unshare_server.handle()
async def unshare_server_handle(bot: Bot, event: GroupMessageEvent):
    if not await GroupHelper.HasPermission(event.group_id, event.user_id):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『共享服务器』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")
    group = Group.get_group(event.group_id)
    if group is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『共享服务器』\n' +
                                "请先加入云黑!\n" +
                                "群内发送'启用云黑'")
        return
    if not group.enable_server_bot:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『共享服务器』\n' +
                                "请启用群机器人!" +
                                "群内发送'启用群机器人'")
    msg = event.get_plaintext().split(" ")
    if len(msg) != 3:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n' +
                               f"格式错误!正确格式: 取消共享服务器 <服务器序号> <共享服务器群号>")
        return
    if not msg[2].isdigit():
        await check_ban.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               + f"QQ群号格式错误!")
        return
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               f"服务器序号错误!")
        return
    if not group.servers[int(msg[1]) - 1].is_owner_server(event.group_id):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               f"只能由服务器拥有群[{group.servers[int(msg[1]) - 1].owner}]才能取消共享!")
        return
    if not int(msg[2]) in group.servers[int(msg[1]) - 1].shared:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『共享服务器』\n'
                               f"本群没有被共享过此服务器!")
        return
    group.servers[int(msg[1]) - 1].shared.remove(int(msg[2]))
    group.servers[int(msg[1]) - 1].update()
    await disconnect(group.servers[int(msg[1]) - 1].token)
    await del_admin.finish(MessageSegment.at(event.user_id) +
                           f'\n『共享服务器』\n'
                           f"取消共享成功!\n")


del_server = on_command("删除服务器")


@del_server.handle()
async def del_server_handle(bot: Bot, event: GroupMessageEvent):
    if not await GroupHelper.HasPermission(event.group_id, event.user_id):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")
        return
    group = Group.get_group(event.group_id)
    if group is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                "请先加入云黑!\n" +
                                "群内发送'启用云黑'")
        return
    if not group.enable_server_bot:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                "请启用群机器人!" +
                                "群内发送'启用群机器人'")
    msg = event.get_plaintext().split(" ")
    if len(msg) != 2:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『删除服务器』\n' +
                               f"格式错误!正确格式: 删除服务器 <服务器序号>")
        return
    cmd = {
        "type": "delserver",
    }
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『删除服务器』\n' +
                               f"删除失败！\n"
                               f"服务器序号错误!")
        return
    if group.servers[int(msg[1]) - 1].is_owner_server(event.group_id):
        if server_available(group.servers[int(msg[1]) - 1].token):
            await send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
        Server.del_server(group.servers[int(msg[1]) - 1].token)
        await disconnect(group.servers[int(msg[1]) - 1].token)
        del group.servers[int(msg[1]) - 1]
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『删除服务器』\n' +
                               f"服务器删除成功!\n"
                               f"若解绑失败，请删除服务器tshock/CaiBot.json然后重启")
    else:
        group.servers[int(msg[1]) - 1].shared.remove(group.id)
        group.servers[int(msg[1]) - 1].update()
        await disconnect(group.servers[int(msg[1]) - 1].token)
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『删除服务器』\n' +
                               f"服务器已被取消共享!")


remote_command = on_command("#", aliases={"远程命令", "远程指令", "c"})


@remote_command.handle()
async def remote_command_handle(bot: Bot, event: GroupMessageEvent):
    msg = GroupHelper.at_to_name(event.raw_message).split(" ", 2)
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 3:
            await add_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『远程指令』\n' +
                                   f"格式错误!正确格式: 远程指令 <服务器序号> <命令内容>")
            return
        if msg[2][0] != "/":
            msg[2] = "/" + msg[2]
        cmd = {
            "type": "cmd",
            "cmd": msg[2],
            "at": str(event.user_id)
        }
        if len(group.servers) == 0:
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『远程指令』\n' +
                                   f"你好像还没有绑定服务器捏？")
        if msg[1] == "all" or msg[1] == "*":
            id = 0
            for i in group.servers:
                id += 1
                if not server_available(i.token):
                    await del_admin.send(MessageSegment.at(event.user_id) +
                                         f'\n『远程指令』\n' +
                                         f"执行失败！\n"
                                         f"❌服务器[{id}]处于离线状态")
                else:
                    await send_data(i.token, cmd, event.group_id)
            return
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『远程指令』\n' +
                                   f"执行失败！\n"
                                   f"服务器序号错误!")
            return
        if not server_available(group.servers[int(msg[1]) - 1].token):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『远程指令』\n' +
                                   f"执行失败！\n"
                                   f"❌服务器[{int(msg[1])}]处于离线状态")
        await send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『远程指令』\n' +
                                "没有权限!")


online = on_command("在线", aliases={"在线人数", "在线查询", "泰拉在线", "查询在线"})


@online.handle()
async def remote_command_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    if len(group.servers) == 0:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『泰拉在线』\n' +
                               f"你好像还没有绑定服务器捏？")
    result = await wait_for_online(event.group_id, group.servers)

    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f'\n『泰拉在线』\n' +
                            "\n".join(result))


bind = on_command("添加白名单", aliases={"绑定"})


@bind.handle()
async def bind_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ")
    msg = [word for word in msg if word]
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is not None and user.name != "":
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "你已经在BOT中绑定过白名单了哦！\n"
                                f"你绑定的角色为[{user.name}]")
        return
    if len(msg) != 2:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "格式错误！\n"
                                f"正确格式: 添加白名单 <名字>")
    user2 = User.get_user_name(msg[1])
    if user2 is not None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "绑定失败!\n"
                                f"这个名字被占用啦！")
        return

    if not TextHandle.check_name(msg[1]):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "绑定失败!\n"
                                f"名字只能含汉字、字母、数字哦！")
        return
    if not msg[1]:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "绑定失败!\n"
                                f"名字不能为空！")
        return
    if user is not None:
        user.name = msg[1]
        user.update()
    else:
        User.add_user(event.user_id, msg[1], event.group_id)

    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f'\n『白名单』\n' +
                            "绑定成功~\n"
                            f"你可以使用[{msg[1]}]进入服务器啦!")


rebind = on_command("修改白名单", aliases={"更改白名单"})


@rebind.handle()
async def rebind_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ")
    msg = [word for word in msg if word]
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None or user.name == "":
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "你还没有在小小Cai这里绑定过白名单哦！\n"
                                f"发送'添加白名单 <名字>'可以进行绑定")
        return
    now = datetime.datetime.today().date()

    days_since_last_rename = (now - user.last_rename.date()).days

    if days_since_last_rename < 30:
        days_left = 30 - days_since_last_rename
        next_rename_date = now + datetime.timedelta(days=days_left)
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "检测到你在这个月修改过一次白名单~\n" +
                                f"{days_left}天之后, 即{next_rename_date}才可以继续修改")
    if len(msg) != 2:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "格式错误！\n"
                                f"正确格式: 修改白名单 <名字>")
    user2 = User.get_user_name(msg[1])
    if user2 is not None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "绑定失败!\n"
                                f"这个名字被占用啦！")
        return

    if not TextHandle.check_name(msg[1]):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "绑定失败!\n"
                                f"名字只能含汉字、字母、数字哦！")
        return
    if not msg[1]:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『白名单』\n' +
                                "绑定失败!\n"
                                f"名字不能为空！")
        return
    user.name = msg[1]
    user.last_rename = datetime.datetime.now()
    user.update()
    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f'\n『白名单』\n' +
                            "重绑成功~\n"
                            f"你可以使用[{msg[1]}]进入服务器啦!\n"
                            f"*小小Cai不会帮你迁移存档，迁移存档请找服主和管理大大~")


un_bind = on_command("删除白名单")


@un_bind.handle()
async def un_bind_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ")
    msg = [word for word in msg if word]
    if event.user_id == 3042538328:
        if len(msg) != 2:
            await agreement3.finish(MessageSegment.at(event.user_id) +
                                    f'\n『白名单』\n' +
                                    "格式错误！\n"
                                    f"正确格式: 删除白名单 <名字>")
        user = User.get_user_name(msg[1])
        if user is not None:
            user.name = ""
            user.update()
            await agreement3.finish(MessageSegment.at(event.user_id) +
                                    f'\n『白名单』\n' +
                                    "解绑成功!\n"
                                    f"QQ:{user.id},处于未绑定状态")
        else:
            await agreement3.finish(MessageSegment.at(event.user_id) +
                                    f'\n『白名单』\n' +
                                    "没有找到玩家!")
            return


sign = on_command("签到")


@sign.handle()
async def sign_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『签到』\n' +
                                "你还没有添加白名单！\n"
                                f"发送'添加白名单 <名字>'来添加白名单")
        return

    def is_today_or_yesterday(dt):
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        return dt.date() in [today, yesterday]

    def is_today(date):
        today = datetime.datetime.now()
        return date.date() == today.date()

    if is_today(user.last_sign):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『签到』\n' +
                                "你今天已经签过到了哦!\n"
                                f"明天再来吧~")
        return
    if is_today_or_yesterday(user.last_sign):
        user.sign_count += 1
    else:
        user.sign_count = 1
    luck = random.randint(0, 100)
    sign_money = random.randint(0, 1000)
    user.money += int(sign_money * (luck / 100 + 1) + user.sign_count * 10)
    if user.last_sign.date() == datetime.datetime.today().date():
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『签到』\n' +
                                "摸摸头,今天你已经签过到了哦!\n"
                                f"明天再来吧~")
        return
    if datetime.datetime.now().hour < 12:
        time_text = "上午好"
    elif datetime.datetime.now().hour == 12:
        time_text = "中午好"
    elif 12 < datetime.datetime.now().hour < 18:
        time_text = "下午好"
    else:
        time_text = "晚上好"
    day = user.sign_count
    text_list = [f"{time_text}呀,今天是你连续签到的第{day}天,额外获得{day * 10}金币",
                 f"{time_text}阁下,今天是你连续签到的第{day}天,额外获得{day * 10}金币",
                 f"{time_text},今天是阁下连续签到的第{day}天,额外获得{day * 10}金币"]
    text = text_list[random.randint(0, 2)]
    if event.get_user_id() == "3042538328":
        text = f"喵喵, 我亲爱的主人阁下,今天是你连续签到的第{day}天哦"
    elif event.get_user_id() == "3383713950":
        text = f"我亲爱的屑法律阁下,今天是你连续爆金币的第{day}天哦"
    user.last_sign = datetime.datetime.now()
    user.update()

    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f'\n『签到』\n' +
                            f"{text}\n"
                            f"今日人品:{luck}\n"
                            f"金币加成:+{luck}%\n"
                            f"获得金币: {int(sign_money * (luck / 100 + 1) + user.sign_count * 10)}\n"
                            f"签到排名: {User.get_sign_rank()}\n\n"
                            f"{await get_hitokoto()}")


bank = on_command("查询金币")


@bank.handle()
async def bank_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『银行』\n' +
                                "你还没有添加白名单！\n"
                                f"发送'添加白名单 <名字>'来添加白名单")
        return
    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f'\n『银行』\n' +
                            f"金币: {user.money}\n"
                            f"连签天数: {user.sign_count}")


world_progress = on_command("进度", aliases={"进度查询", "查询进度"})


@world_progress.handle()
async def world_progress_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    msg = event.get_plaintext().split(" ")
    text = [word for word in msg if word]
    if len(text) == 2:
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『进度查询』\n' +
                                   f"获取失败！\n"
                                   f"服务器序号错误!")
            return
        num = text[1]
        if not server_available(group.servers[int(msg[1]) - 1].token):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『进度查询』\n' +
                                   f"执行失败！\n"
                                   f"❌服务器[{int(msg[1])}]处于离线状态")
        cmd = {
            "type": "process"
        }
        await send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『进度查询』\n'
                               f'查询失败！\n'
                               f'格式错误！正确格式: 进度查询 [服务器序号]')


def is_within_5_minutes(your_datetime):
    # 获取当前时间
    current_time = datetime.datetime.now()

    # 计算时间差
    time_difference = current_time - your_datetime

    # 检查时间差是否小于5分钟
    if time_difference < datetime.timedelta(minutes=5):
        return True
    else:
        return False


ac = on_command('登录', aliases={"批准", "允许", "登陆"})


@ac.handle()
async def acf(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『登录系统』\n' +
                                "你还没有添加白名单！\n"
                                f"发送'添加白名单 <名字>'来添加白名单")
        return
    if user.login_request.time == datetime.datetime.min:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f"\n『登录系统』\n"
                                f"你目前没有收到任何登录请求！")
        return
    if not is_within_5_minutes(user.login_request.time):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f"\n『登录系统』\n"
                                f"登录请求已失效！")
    user.uuid.append(user.login_request.uuid)
    user.login_request = LoginRequest(datetime.datetime.min, "")
    user.update()
    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f"\n『登录系统』\n"
                            f"✅已接受此登录请求！\n"
                            f"使用'清空设备'解除所有绑定")


ds = on_command('拒绝', aliases={"不批准", "不允许"})


@ds.handle()
async def dsf(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『登录系统』\n' +
                                "你还没有添加白名单！\n"
                                f"发送'添加白名单 <名字>'来添加白名单")
        return

    if user.login_request.time == datetime.datetime.min:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f"\n『登录系统』\n"
                                f"你目前没有收到任何登录请求！")
        return
    if not is_within_5_minutes(user.login_request.time):
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f"\n『登录系统』\n"
                                f"登录请求已失效！")
    user.login_request = LoginRequest(datetime.datetime.min, "")
    user.update()
    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f"\n『登录系统』\n"
                            f"❌已拒绝此批准！")
    return


de = on_command('清空设备', aliases={"清除绑定"})


@de.handle()
async def deff(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『登录系统』\n' +
                                "你还没有添加白名单！\n"
                                f"发送'添加白名单 <名字>'来添加白名单")
        return
    user.uuid = []
    user.update()
    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f"\n『登录系统』\n"
                            f"你已清空所有绑定设备！")


update = \
    """🧪适配插件下载: https://wwf.lanzouj.com/b0mahl2xg 密码:2pdn
🌐安装教程: https://tr.monika.love/resources/118/
"""

help = on_command("菜单")


@help.handle()
async def help_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help.finish(MessageSegment.at(event.user_id) +
                      f'\n『菜单』\n'
                      f'⚡服务器管理\n'
                      f'⚡快捷功能菜单\n'
                      f'⚡地图功能菜单\n'
                      f'⚡白名单菜单\n\n'
                      + update)


help1 = on_command("服务器管理")


@help1.handle()
async def help1_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help.finish(MessageSegment.at(event.user_id) +
                      f'\n『菜单•服务器管理』\n'
                      f'⚡添加服务器 <IP地址> <端口> <验证码>\n'
                      f'⚡删除服务器 <服务器序号> \n'
                      f'⚡共享服务器 <服务器序号> <群号>\n'
                      f'⚡取消共享服务器 <服务器序号> <群号>\n'
                      f'⚡服务器列表 [获取服务器地址端口等]\n'
                      f'⚡服务器信息 <服务器序号> [获取服务器详细信息]')


help2 = on_command("快捷功能菜单")


@help2.handle()
async def help2_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help.finish(MessageSegment.at(event.user_id) +
                      f'\n『菜单•快捷功能』\n'
                      f'⚡添加白名单 <名字> [绑定角色]\n'
                      f'⚡修改白名单 <名字> [重新绑定角色]\n'
                      f'⚡远程指令 <服务器序号> <命令内容> [执行远程命令]\n'
                      f'⚡在线 [获取服务器在线]\n'
                      f'⚡服务器列表 [获取服务器地址端口等]\n'
                      f'⚡进度查询 <服务器序号>\n'
                      f'⚡查背包 <服务器序号> <玩家名> [查询玩家的背包内容]\n'
                      f'⚡查绑定 <玩家名/玩家QQ> [查询绑定]\n'
                      f'⚡wiki <搜索内容> [查询Wiki]\n'
                      f'⚡清空设备 [清除绑定的设备]\n'
                      f'⚡自踢 [断开所有服务器连接]')


help3 = on_command("地图功能菜单")


@help3.handle()
async def help3_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help.finish(MessageSegment.at(event.user_id) +
                      f'\n『菜单•地图功能』\n'
                      f'⚡查看地图 <服务器序号> [获取地图图片]\n'
                      f'⚡下载地图  <服务器序号> [获取地图文件(可能不可用)]\n'
                      f'⚡下载小地图  <服务器序号> [获取点亮的小地图文件]')


help4 = on_command("白名单菜单")


@help4.handle()
async def help_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help4.finish(MessageSegment.at(event.user_id) +
                       f'\n『菜单•白名单』\n'
                       f'⚡签到 [没啥用]\n'
                       f'⚡查询金币 [字面意思]\n'
                       f'⚡添加白名单 <名字> [绑定角色]\n'
                       f'⚡修改白名单 <名字> [重新绑定角色]')


wiki = on_startswith(("搜索", "wiki", "Wiki", "WIKI"))


@wiki.handle()
async def wiki_(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    msg = event.get_plaintext().replace("搜索 ", "").replace("wiki ", "").replace("Wiki ", "").replace("WIKI ",
                                                                                                       "").replace(
        "搜索", "").replace("wiki", "").replace("Wiki", "").replace("WIKI", "")
    if msg == "":
        await wiki.finish(MessageSegment.at(event.user_id) +
                          f"\n『Terrariab Wiki』\n"
                          f"已为你找到以下TerrariaWiki网站：\n1"
                          f"⃣官方百科：\nhttps://terraria.wiki.gg/zh/wiki/Terraria_Wiki\n"
                          f"2⃣旧百科：\nhttps://terraria.fandom.com/zh/wiki/Terraria_Wiki\n"
                          f"3⃣灾厄百科：\nhttps://calamitymod.wiki.gg/zh")
    await wiki.finish(MessageSegment.at(event.user_id) +
                      f"\n『TerrariaWiki』\n"
                      f"已从Wiki上帮你找到[{msg}]，点击对应链接查看：\n1"
                      f"⃣官方百科：\nhttps://terraria.wiki.gg/zh/wiki/{parse.quote(msg)}\n"
                      f"2⃣旧百科：\nhttps://terraria.fandom.com/zh/wiki/Special:%E6%90%9C%E7%B4%A2?search={parse.quote(msg)}\n"
                      f"3⃣灾厄百科：\nhttps://calamitymod.wiki.gg/zh/index.php?search={parse.quote(msg)}")


find_player = on_command("查绑定", aliases={"查询绑定", "绑定查询"})


@find_player.handle()
async def find_player_function(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    message_text = GroupHelper.replace_at(event.raw_message)
    msg = message_text.split(" ")
    msg = [word for word in msg if word]
    if len(msg) == 2:
        user = None
        try:
            user = User.get_user(int(msg[1]))
        except:
            pass
        user2 = User.get_user_name(msg[1])

        if user is None and user2 is None:
            await find_player.finish(MessageSegment.at(event.user_id) +
                                     f"\n『查绑定』\n"
                                     f"查询失败！\n"
                                     f"没有找到与[{msg[1]}]有关的信息")
            return
        if user is not None and user2 is not None:
            await find_player.finish(MessageSegment.at(event.user_id) +
                                     f"\n『查绑定』\n"
                                     f"查询成功！\n"
                                     f"#⃣QQ[{user.id}]\n"
                                     f"绑定角色[{user.name}]\n"
                                     f"#⃣QQ[{user2.id}]\n"
                                     f"绑定角色[{user2.name}]")
            return
        if user is not None:
            await find_player.finish(MessageSegment.at(event.user_id) +
                                     f"\n『查绑定』\n"
                                     f"查询成功！\n"
                                     f"#⃣QQ[{user.id}]\n"
                                     f"绑定角色[{user.name}]")
            return
        if user2 is not None:
            await find_player.finish(MessageSegment.at(event.user_id) +
                                     f"\n『查绑定』\n"
                                     f"查询成功！\n"
                                     f"#⃣QQ[{user2.id}]\n"
                                     f"绑定角色[{user2.name}]")
            return
    else:
        await find_player.finish(MessageSegment.at(event.user_id) +
                                 "\n『查绑定』\n"
                                 "格式错误！\n"
                                 "正确格式：查绑定 [角色名字]/[QQ号]")


self_kick = on_command("自踢", aliases={"自提", "自体"})


@self_kick.handle()
async def self_kick_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『自踢』\n' +
                                "你还没有添加白名单！\n"
                                f"发送'添加白名单 <名字>'来添加白名单")
        return
    cmd = {
        "type": "selfkick",
        "name": user.name
    }
    for i in group.servers:
        await send_data(i.token, cmd, event.group_id)
    await self_kick.finish(MessageSegment.at(event.user_id) +
                           f'\n『自踢』\n' +
                           f"自踢成功！")


broadcast = on_command("群发消息")


@broadcast.handle()
async def broadcast_handle(bot: Bot, event: GroupMessageEvent):
    if event.user_id == 3042538328:
        msg = event.get_plaintext().split(" ", 1)
        msg = msg[1]
        await GroupHelper.send_all_groups(msg)


get_map_png = on_command("查看地图")


@get_map_png.handle()
async def get_map_png_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ")
    group = Group.get_group(event.group_id)
    if not group.enable_server_bot:
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 2:
            await add_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『查看地图』\n' +
                                   f"格式错误!正确格式: 查看地图 <服务器序号>")
            return
        cmd = {
            "type": "mappng"
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『查看地图』\n' +
                                   f"获取失败！\n"
                                   f"服务器序号错误!")
            return
        if not server_available(group.servers[int(msg[1]) - 1].token):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『查看地图』\n' +
                                   f"获取失败！\n"
                                   f"❌服务器[{int(msg[1])}]处于离线状态")
        try:
            server = get_server(group.servers[int(msg[1]) - 1].token)
            if server.terraria_version.startswith("tModLoader"):
                await del_admin.finish(MessageSegment.at(event.user_id) +
                                       f'\n『查看地图』\n' +
                                       f"获取失败！\n"
                                       f"❌不支持tModLoader服务器")
                return
        except:
            pass

        await send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『查看地图』\n' +
                                "没有权限!")


get_world_file = on_command("下载地图")


@get_world_file.handle()
async def get_world_file_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ")
    group = Group.get_group(event.group_id)
    if not group.enable_server_bot:
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 2:
            await add_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『下载地图』\n' +
                                   f"格式错误!正确格式: 下载地图 <服务器序号>")
            return
        cmd = {
            "type": "worldfile"
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『下载地图』\n' +
                                   f"获取失败！\n"
                                   f"服务器序号错误!")
            return
        if not server_available(group.servers[int(msg[1]) - 1].token):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『下载地图』\n' +
                                   f"获取失败！\n"
                                   f"❌服务器[{int(msg[1])}]处于离线状态")
        await send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『下载地图』\n' +
                                "没有权限!")


get_map_file = on_command("下载小地图")


@get_map_file.handle()
async def get_world_file_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ")
    group = Group.get_group(event.group_id)
    if not group.enable_server_bot:
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 2:
            await add_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『下载小地图』\n' +
                                   f"格式错误!正确格式: 下载小地图 <服务器序号>")
            return
        cmd = {
            "type": "mapfile"
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『下载小地图』\n' +
                                   f"获取失败！\n"
                                   f"服务器序号错误!")
            return
        if not server_available(group.servers[int(msg[1]) - 1].token):
            await del_admin.finish(MessageSegment.at(event.user_id) +
                                   f'\n『下载小地图』\n' +
                                   f"获取失败！\n"
                                   f"❌服务器[{int(msg[1])}]处于离线状态")
        await send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await agreement3.finish(MessageSegment.at(event.user_id) +
                                f'\n『下载小地图』\n' +
                                "没有权限!")


ban_list = on_command("云黑列表")


@ban_list.handle()
async def ban_list_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await ban_list.finish(MessageSegment.at(event.user_id) +
                              f'\n『云黑列表』\n'
                              + "请启用云黑!\n"
                                "发送'启用云黑'在本群启用本BOT")
        return
    msg = event.get_plaintext().split(" ")
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
                              "⚠检测到云黑记录:\n" +
                              "\n".join(bans) +
                              "\n翻页：云黑列表 <页码>")

    return


random_ban = on_command("随机云黑")


@random_ban.handle()
async def random_ban_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await random_ban.finish(MessageSegment.at(event.user_id) +
                                f'\n『随机云黑』\n'
                                + "请启用云黑!\n"
                                  "发送'启用云黑'在本群启用本BOT")
        return

    result = UserBan.get_all_bans()
    ban = random.choice(result)

    await random_ban.finish(MessageSegment.at(event.user_id) +
                            f'\n『随机云黑』\n' +
                            f'⚠检测到云黑记录({ban.id})\n' +
                            f'\n'.join([await x.to_string() for x in
                                        ban.bans]))


group_ban_list = on_command("群云黑列表")


@group_ban_list.handle()
async def group_ban_list_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『随机云黑』\n'
                                    + "请启用云黑!\n"
                                      "发送'启用云黑'在本群启用本BOT")
        return

    msg = event.get_plaintext().split(" ")
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
            return

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
                                    "⚠检测到云黑记录:\n" +
                                    f'\n'.join([await x.to_group_string() for x in
                                                bans]))


group_ban_list = on_command("群云黑清空")


@group_ban_list.handle()
async def group_ban_list_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『随机云黑』\n'
                                    + "请启用云黑!\n"
                                      "发送'启用云黑'在本群启用本BOT")
        return
    if not await GroupHelper.is_admin(FEED_BACK_GROUP,event.user_id):
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑删除』\n'
                                    + "没有权限")
        return
    msg = event.get_plaintext().split(" ", 1)
    group_num = 0
    if len(msg) != 2:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑删除』\n'
                                    + "格式错误!正确格式: 群云黑清空 <QQ群号>")
    else:
        try:
            group_num = int(msg[1])
        except ValueError:
            await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                        f'\n『云黑删除』\n'
                                        + "格式错误!无效QQ群号")
            return

    result = UserBan.get_all_bans()
    bans = []
    for i in result:
        for n in i.bans:
            if n.group == group_num:
                n.id = i.id
                bans.append(n)
                i.del_ban(group_num)

    if len(bans) == 0:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑删除({group_num})』\n'
                                    + "检测到任何记录!")
    else:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑删除({group_num})』\n' +
                                    "✅已删除记录:\n" +
                                    f'\n'.join([await x.to_group_string() for x in
                                                bans]))


group_ban_list = on_command("群云黑封禁")


@group_ban_list.handle()
async def group_ban_list_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群云黑封禁』\n'
                                    + "请启用云黑!\n"
                                      "发送'启用云黑'在本群启用本BOT")
        return
    if not await GroupHelper.is_admin(FEED_BACK_GROUP,event.user_id):
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群云黑封禁』\n'
                                    + "没有权限")
        return
    msg = event.get_plaintext().split(" ")
    if len(msg) != 2:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群云黑封禁』\n'
                                    + "格式错误!正确格式: 群云黑封禁 <QQ群号>")
    else:
        try:
            group_num = int(msg[1])
        except ValueError:
            await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                        f'\n『群云黑封禁』\n'
                                        + "格式错误!无效QQ群号")
            return

    target_group = Group.get_group(group_num)
    if group is None:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群云黑封禁』\n'
                                    + "本群没有使用CaiBot捏\n")
        return
    if target_group.reject_edition:
        target_group.reject_edition = False
        target_group.update()
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群云黑封禁({group_num})』\n'
                                    + "已解除添加云黑限制!")
    else:
        target_group.reject_edition = True
        target_group.update()
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『群云黑封禁({group_num})』\n'
                                    + "已禁止其添加云黑!")




group_ban_list = on_command("群云黑删除")


@group_ban_list.handle()
async def group_ban_list_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『随机云黑』\n'
                                    + "请启用云黑!\n"
                                      "发送'启用云黑'在本群启用本BOT")
        return
    if not await GroupHelper.is_admin(FEED_BACK_GROUP,event.user_id):
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑删除』\n'
                                    + "没有权限")
        return
    msg = event.get_plaintext().split(" ")
    group = 0
    target = 0
    if len(msg) != 3:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑删除』\n'
                                    + "格式错误!正确格式: 群云黑删除 <QQ号> <QQ群号>")
    else:
        try:
            target = int(msg[1])
            group = int(msg[2])
        except ValueError:
            await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                        f'\n『云黑删除』\n'
                                        + "格式错误!无效QQ群号或QQ号")
            return

    result = UserBan.get_all_bans()
    bans = []
    for i in result:
        for n in i.bans:
            if i.id == target and n.group == group:
                n.id = i.id
                bans.append(n)
                i.del_ban(group)

    if len(bans) == 0:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑删除({group}=>{target})』\n'
                                    + "检测到任何记录!")
    else:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『云黑删除({group}=>{target})』\n' +
                                    "✅已删除记录:\n" +
                                    f'\n'.join([await x.to_group_string() for x in
                                                bans]))


look_bag = on_command("查背包", aliases={"查看背包", "查询背包"})


@look_bag.handle()
async def look_bag_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    msg = GroupHelper.at_to_name(event.raw_message).split(" ")
    if not group.enable_server_bot:
        return

    if len(msg) != 3:
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『查背包』\n' +
                               f"格式错误!正确格式: 查背包 <服务器序号> <玩家名>")
        return
    cmd = {
        "type": "lookbag",
        "name": msg[2],
    }
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『查背包』\n' +
                               f"查询失败！\n"
                               f"服务器序号错误!")
        return
    if not server_available(group.servers[int(msg[1]) - 1].token):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『查背包』\n' +
                               f"查询失败！\n"
                               f"❌服务器[{int(msg[1])}]处于离线状态")
    await send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)


lookfor = on_command("lookfor")


@lookfor.handle()
async def lookfor_handle(bot: Bot, event: GroupMessageEvent):
    if event.user_id != 3042538328:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『LookFor』\n'
                                    + "没有权限")
        return
    msg = GroupHelper.at_to_name(event.raw_message).split(" ")
    group_num = 0
    if len(msg) != 2:
        await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                    f'\n『LookFor』\n'
                                    + "格式错误!正确格式: LookFor <QQ号>")
    else:
        try:
            qq_num = int(msg[1])
        except ValueError:
            await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                        f'\n『LookFor』\n'
                                        + "格式错误!无效QQ号")
            return
        result = await GroupHelper.look_for_from_groups(qq_num)
        lines = []
        for i in result:
            lines.append(f"{i[0]}({i[1]})")
        if len(lines) == 0:
            await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                        f'\n『LookFor』\n'
                                        + f"[{qq_num}]不在小小Cai加入的任何群中")
        else:
            await group_ban_list.finish(MessageSegment.at(event.user_id) +
                                        f'\n『LookFor』\n'
                                        + f"[{qq_num}]的查询结果:\n"
                                        + "\n".join(lines))


ping = on_command("ping")


@ping.handle()
async def ping_handle(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().split(" ")
    if len(msg) != 3:
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『PING』\n' +
                               f"格式错误!正确格式: ping <服务器地址> <端口>")
        return
    try:
        adr = socket.gethostbyname(msg[1])
    except:
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『PING』\n' +
                               f"没有找到服务器欸？")
        return

    try:
        time, packid = await ping_server(adr, int(msg[2]))
    except TimeoutError:
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『PING』\n' +
                               f"服务器连接超时！")
        return
    except Exception as ex:
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『PING』\n' +
                               f"连接失败！\n错误：{str(ex)}")
        return
    packid = str(packid)
    if packid == "2":
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『PING』\n' +
                               f"PING到服务器啦!\n"
                               f"延迟: {time:.2f}ms, 响应数据包：{packid}\n"
                               f"然后小小Cai被服务器一脚踢了出去，呜呜呜...")
        return
    if packid != "LegacyMultiplayer4" and packid != "3":
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『PING』\n' +
                               f"PING到服务器啦!\n"
                               f"延迟: {time:.2f}ms, 响应数据包：{packid}\n"
                               f"但是小小Cai发现这好像不是Terraria服务器？")
        return
    await add_admin.finish(MessageSegment.at(event.user_id) +
                           f'\n『PING』\n' +
                           f"PING到服务器啦!\n"
                           f"延迟: {time:.2f}ms, 响应数据包：{packid}")


server_list = on_command("服务器列表", aliases={"ip", "IP"})


@server_list.handle()
async def server_list_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    result = []
    id = 1
    for i in group.servers:
        if server_available(i.token):
            # 『服务器列表』
            # ๑1๑cai的喵窝(v1.4.4.9)
            try:
                server = get_server(i.token)
                server_version = server.terraria_version
                world = server.world
                if (server.whitelist):
                    white_list = "[Cai白名单]"
                else:
                    white_list = ""
                result.append(f"๑{id}๑🌐{world}{white_list}({server_version})\n地址：{i.ip}\n端口：{i.port}")
            except:
                result.append(f"๑{id}๑🌐请更新CaiBOT插件哦~\n地址：{i.ip}\n端口：{i.port}")

        else:
            result.append(f"๑{id}๑❌服务器处于离线状态")
        id += 1
    await agreement3.finish(MessageSegment.at(event.user_id) +
                            f'\n『泰拉在线』\n' +
                            "\n".join(result))


server_info = on_command("服务器信息")


@server_info.handle()
async def server_info_handle(bot: Bot, event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    msg = GroupHelper.at_to_name(event.raw_message).split(" ")
    if not group.enable_server_bot:
        return

    if len(msg) != 2:
        await add_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『服务器信息』\n' +
                               f"格式错误!正确格式: 服务器信息 <服务器序号>")
        return
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『服务器信息』\n' +
                               f"查询失败！\n"
                               f"服务器序号错误!")
        return
    if not server_available(group.servers[int(msg[1]) - 1].token):
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『服务器信息』\n' +
                               f"查询失败！\n"
                               f"❌服务器[{int(msg[1])}]处于离线状态")
    i = group.servers[int(msg[1]) - 1]
    try:
        # "tshock_version":"5.2.0.0","plugin_version":"2024.6.7.0","terraria_version":"v1.4.4.9","whitelist":false,"os":"win10-x64"
        server = get_server(i.token)
        server_version = server.terraria_version
        world = server.world
        tshock_version = server.tshock_version
        whitlist = server.whitelist
        plugin_version = server.plugin_version
        os = server.os
        await del_admin.send(MessageSegment.at(event.user_id) +
                             f'\n『服务器信息』\n' +
                             f"服务器[{int(msg[1])}]的详细信息: \n"
                             f"地址: {i.ip}:{i.port}\n"
                             f"世界名: {world}\n"
                             f"Terraria版本: {server_version}\n"
                             f"TShock版本: {tshock_version}\n"
                             f"CaiBot扩展版本: {plugin_version}\n"
                             f"Cai白名单: {whitlist}\n"
                             f"服务器系统: {os}")
        return
    except:
        await del_admin.finish(MessageSegment.at(event.user_id) +
                               f'\n『服务器信息』\n' +
                               f"服务器[{int(msg[1])}]的详细信息: \n"
                               f"地址: {i.ip}:{i.port}\n"
                               f"🌐详细信息获取失败,请更新CaiBOT插件哦~")
