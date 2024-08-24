import re
import requests
from nonebot import on_request, on_notice
from nonebot.adapters.onebot.v11 import MessageSegment, Event, Bot, GroupRequestEvent, GroupIncreaseNoticeEvent, \
    FriendRequestEvent, RequestEvent

import utils.statistics
from utils.ban_user import UserBan
from utils.statistics import Statistics

dict1 = {}

FEEDBACK_GROUP = 991556763
TSHOCK_GROUP = 816771079


def _check2(event: Event):
    return isinstance(event, RequestEvent)


request = on_request(rule=_check2)


@request.handle()
async def _(event: RequestEvent, bot: Bot):
    if event.request_type == "friend":
        await bot.call_api("set_friend_add_request", flag=event.flag, approve=True)
        return
    if event.sub_type == 'invite':
        await bot.call_api("set_group_add_request", flag=event.flag, sub_type=event.sub_type,
                           approve=True)


def _check0(event: Event):
    return isinstance(event, GroupRequestEvent)


request = on_request(rule=_check0)


@request.handle()
async def _(event: GroupRequestEvent, bot: Bot):
    Statistics.add_check()
    if event.group_id == FEEDBACK_GROUP:
        return
    ban = UserBan.get_user(event.user_id)
    if ban is not None and len(ban.bans) > 1:
        await bot.call_api("set_group_add_request", flag=event.flag, sub_type=event.sub_type,
                           approve=False, reason='你已被加入云黑名单，无法加入此服务器群!')
        await bot.call_api("send_group_msg", group_id=event.group_id, message=
        f'『云黑名单•拒绝加入』\n' +
        f'❌检测到云黑记录({event.user_id})\n' +
        f'\n'.join([await x.to_string() for x in
                    ban.bans]))
        ban.has_kicked += 1
        ban.update()
        Statistics.add_kick()
        await request.finish()
    if ban is not None and ban.check_ban(event.group_id):
        await bot.call_api("set_group_add_request", flag=event.flag, sub_type=event.sub_type,
                           approve=False, reason='你已被加入此群黑名单，无法加入此服务器群!')
        await bot.call_api("send_group_msg", group_id=event.group_id, message=
        f'『云黑名单•拒绝加入』\n' +
        f'❌检测到云黑记录({event.user_id})\n' +
        f'\n'.join([await x.to_string() for x in
                    ban.bans]))
        ban.has_kicked += 1
        ban.update()
        Statistics.add_kick()
        await request.finish()


def _check1(event: Event):
    return isinstance(event, GroupIncreaseNoticeEvent)


tshock_guide = """📖开服基础教程
• TS开服基础教程: https://tr.monika.love/docs/tshock-tutorial-1
• TS仓库: https://github.com/Pryaxis/TShock/releases
📘TS相关文档
• TS中文文档(熙恩版): http://tsdoc.terraria.ink
• 官方英文文档: https://ikebukuro.tshock.co/#
• 插件开发指南(Cai版): https://gitee.com/e7udyuu/tshock-plugin-document
• 插件开发教程(RenderBr版): https://github.com/RenderBr/TShockTutorials
💊TS插件库
• GitHub仓库: https://github.com/UnrealMultiple/TShockPlugin
• Gitee仓库(镜像): https://gitee.com/kksjsj/TShockPlugin
• 插件包下载: http://plugins.terraria.ink
• 官方插件库: https://github.com/Pryaxis/Plugins
🔭论坛插件资源
• https://tr.monika.love
• https://trhub.cn
• https://bbstr.net
❤️ Powered by 熙恩"""

incr = on_notice(rule=_check1)


@incr.handle()
async def _(event: GroupIncreaseNoticeEvent, bot: Bot, ):
    ban = UserBan.get_user(event.user_id)
    Statistics.add_check()

    if event.group_id == TSHOCK_GROUP:
        await bot.call_api("send_group_msg", group_id=event.group_id, message=MessageSegment.at(event.user_id) +
                                                                              f'\n『欢迎加入TShock官方群』\n' + tshock_guide)
        return
    if ban is not None and len(ban.bans) > 0:
        if event.group_id == FEEDBACK_GROUP:
            await bot.call_api("send_group_msg", group_id=event.group_id, message=MessageSegment.at(event.user_id) +
                                                                                  f'\n『欢迎加入CaiBot群』\n' +
                                                                                  '⚠检测到云黑记录({event.user_id})\n' +
                                                                                  f'\n'.join(
                                                                                      [await x.to_string() for x in
                                                                                       ban.bans]))
            return
        await bot.call_api("send_group_msg", group_id=event.group_id, message=MessageSegment.at(event.user_id) +
                                                                              f'\n『云黑名单』\n' +
                                                                              f'⚠检测到云黑记录({event.user_id})\n' +
                                                                              f'\n'.join([await x.to_string() for x in
                                                                                          ban.bans]))
    else:
        statistics = Statistics.get_statistics()
        if event.group_id == FEEDBACK_GROUP:
            await bot.call_api("send_group_msg", group_id=event.group_id, message=MessageSegment.at(event.user_id) +
                                                                                  f'\n『欢迎加入CaiBot群』\n' +
                                                                                  f'✅没有检测到云黑记录({event.user_id})!\n' +
                                                                                  f'本机器人已检查{statistics.total_check}名用户,拒绝{statistics.total_kick}人加群.')
            return
        await bot.call_api("send_group_msg", group_id=event.group_id, message=MessageSegment.at(event.user_id) +
                                                                              '\n『云黑名单』\n' +
                                                                              f'✅没有检测到云黑记录({event.user_id})!\n' +
                                                                              f'本机器人已检查{statistics.total_check}名用户,拒绝{statistics.total_kick}人加群.')
