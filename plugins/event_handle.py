from nonebot import on_request, on_notice
from nonebot.adapters.onebot.v11 import MessageSegment, Event, Bot, GroupRequestEvent, GroupIncreaseNoticeEvent, \
    RequestEvent, GroupBanNoticeEvent

from common.ban_user import UserBan
from common.global_const import FEEDBACK_GROUP, TSHOCK_GROUP
from common.group_helper import GroupHelper
from common.statistics import Statistics

def is_request_event(event: Event) -> bool:
    return isinstance(event, RequestEvent)

def is_group_request_event(event: Event) -> bool:
    return isinstance(event, GroupRequestEvent)

def group_increase_notice_event(event: Event) -> bool:
    return isinstance(event, GroupIncreaseNoticeEvent)

def is_group_ban(event: Event) -> bool:
    return isinstance(event, GroupBanNoticeEvent)



request = on_request(rule=is_request_event)


@request.handle()
async def request_handle(event: RequestEvent, bot: Bot):
    if event.request_type == "friend":
        await bot.call_api("set_friend_add_request", flag=event.flag, approve=True)
        return
    if event.sub_type == 'invite':
        await bot.call_api("set_group_add_request", flag=event.flag, sub_type=event.sub_type,
                           approve=True)


has_reject = []

group_join = on_request(rule=is_group_request_event)


@group_join.handle()
async def group_join_handle(event: GroupRequestEvent, bot: Bot):
    Statistics.add_check()
    if event.group_id == FEEDBACK_GROUP:
        return

    if await GroupHelper.is_superadmin(event.user_id):
        await bot.call_api("set_group_add_request", flag=event.flag, sub_type=event.sub_type,
                           approve=True)
        await bot.call_api("send_group_msg", group_id=event.group_id, message=
        f'『自动批准』\n' +
        f'[{event.user_id}]是CaiBot管理成员.')
        return

    user_ban = UserBan.get_user(event.user_id)
    if user_ban is not None and len(user_ban.bans) > 1:
        await bot.call_api("set_group_add_request", flag=event.flag, sub_type=event.sub_type,
                           approve=False, reason='你已被加入云黑名单，无法加入此服务器群!')
        if event.group_id + event.user_id not in has_reject:
            has_reject.append(event.group_id + event.user_id)
            await bot.call_api("send_group_msg", group_id=event.group_id, message=
            f'『云黑名单•拒绝加入』\n' +
            f'❌检测到云黑记录({event.user_id})\n' +
            f'\n'.join([await x.to_string() for x in
                        user_ban.bans]))
        user_ban.has_kicked += 1
        user_ban.update_user()
        Statistics.add_kick()
        await request.finish()
    if user_ban is not None and user_ban.check_ban(event.group_id):
        await bot.call_api("set_group_add_request", flag=event.flag, sub_type=event.sub_type,
                           approve=False, reason='你已被加入此群黑名单，无法加入此服务器群!')
        if event.group_id + event.user_id not in has_reject:
            has_reject.append(event.group_id + event.user_id)
            await bot.call_api("send_group_msg", group_id=event.group_id, message=
            f'『云黑名单•拒绝加入』\n' +
            f'❌检测到云黑记录({event.user_id})\n' +
            f'\n'.join([await x.to_string() for x in
                        user_ban.bans]))
        user_ban.has_kicked += 1
        user_ban.update_user()
        Statistics.add_kick()
        await request.finish()





tshock_guide = """📖必看文档
• TS开服基础教程: https://tr.monika.love/docs/tshock-tutorial-1
• 插件文档: http://docs.terraria.ink/zh
📘TS相关文档
• TS中文文档(熙恩版): http://tsdoc.terraria.ink
• 官方英文文档: https://github.com/Pryaxis/TShock/wiki
• 插件开发指南(Cai版): http://docs.terraria.ink/zh/plugin-dev/get-start.html
• 插件开发教程(RenderBr版): https://github.com/RenderBr/TShockTutorials/wiki
💊TS插件库
• GitHub仓库: https://github.com/UnrealMultiple/TShockPlugin
• 插件包下载: http://plugins.terraria.ink
• 插件文档: http://docs.terraria.ink/zh
🔭论坛插件资源
• https://tr.monika.love
• https://trhub.cn
• https://bbstr.net
❤️ Powered by 熙恩 & Cai"""

incr = on_notice(rule=group_increase_notice_event)


@incr.handle()
async def _(event: GroupIncreaseNoticeEvent, bot: Bot):
    if event.user_id == 2990574917:
        await bot.call_api("send_group_msg", group_id=event.group_id, message=MessageSegment.at(event.user_id) +
                                                                              f'\n『欢迎使用CaiBot』\n'
                                                                              f'📖CaiBot默认开启云黑检测功能,其他功能看下面链接哦~\n'
                                                                              f'🔭教程: https://tr.monika.love/resources/118/\n'
                                                                              f'❤️ Developed by Cai & Contributors')
        return
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
                                                                                  f'⚠检测到云黑记录({event.user_id})\n' +
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



# 感谢未琉
ban = on_notice(rule=is_group_ban)
@ban.handle()
async def handle_group_ban(bot: Bot, event: GroupBanNoticeEvent):
    if event.user_id == event.self_id and event.group_id not in [FEEDBACK_GROUP, TSHOCK_GROUP, 1134311185]:
        group_id = event.group_id
        duration = event.duration
        if duration > 0:
            await bot.set_group_leave(group_id=group_id)