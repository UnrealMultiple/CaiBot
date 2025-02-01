import datetime

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

import plugins.cai_api
from common.group import Group
from common.user import User, LoginRequest

def is_within_5_minutes(your_datetime):
    current_time = datetime.datetime.now()
    time_difference = current_time - your_datetime
    if time_difference < datetime.timedelta(minutes=5):
        return True
    else:
        return False


login = on_command('登录', aliases={"批准", "允许", "登陆"}, force_whitespace=True)


@login.handle()
async def login_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await login.finish(MessageSegment.at(event.user_id) +
                           f'\n『登录系统』\n' +
                           "你还没有添加白名单！\n"
                           f"发送'添加白名单 <名字>'来添加白名单")
    if user.id not in plugins.cai_api.login_requests or plugins.cai_api.login_requests[user.id].time == datetime.datetime.min:
        await login.finish(MessageSegment.at(event.user_id) +
                           f"\n『登录系统』\n"
                           f"你目前没有收到任何登录请求！")
    if not is_within_5_minutes(plugins.cai_api.login_requests[user.id].time):
        await login.finish(MessageSegment.at(event.user_id) +
                           f"\n『登录系统』\n"
                           f"登录请求已失效！")
    user.uuid.append(plugins.cai_api.login_requests[user.id].uuid)
    if len(user.uuid) > 10:
        user.uuid.pop(0)
    user.update()
    plugins.cai_api.login_requests[user.id] = LoginRequest(datetime.datetime.min, "")
    await login.finish(MessageSegment.at(event.user_id) +f"\n『登录系统』\n"
                       f"✅已接受此登录请求！\n"
                       f"使用'清空设备'解除所有绑定")


reject_login = on_command('拒绝', aliases={"不批准", "不允许"}, force_whitespace=True)


@reject_login.handle()
async def reject_login_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await reject_login.finish(MessageSegment.at(event.user_id) +
                                  f'\n『登录系统』\n' +
                                  "你还没有添加白名单！\n"
                                  f"发送'添加白名单 <名字>'来添加白名单")
    if user.id not in plugins.cai_api.login_requests or plugins.cai_api.login_requests[
        user.id].time == datetime.datetime.min:
        await login.finish(MessageSegment.at(event.user_id) +
                           f"\n『登录系统』\n"
                           f"你目前没有收到任何登录请求！")
    if not is_within_5_minutes(plugins.cai_api.login_requests[user.id].time):
        await login.finish(MessageSegment.at(event.user_id) +f"\n『登录系统』\n"
                           f"登录请求已失效！")

    plugins.cai_api.login_requests[user.id] = LoginRequest(datetime.datetime.min, "")
    await reject_login.finish(MessageSegment.at(event.user_id) +
                              f"\n『登录系统』\n"
                              f"❌已拒绝此登录请求！")


clean_device = on_command('清空设备', aliases={"清除绑定"}, force_whitespace=True)


@clean_device.handle()
async def clean_device_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await clean_device.finish(MessageSegment.at(event.user_id) +
                                  f'\n『登录系统』\n' +
                                  "你还没有添加白名单！\n"
                                  f"发送'添加白名单 <名字>'来添加白名单")
    user.uuid = []
    user.update()
    await clean_device.finish(MessageSegment.at(event.user_id) +
                              f"\n『登录系统』\n"
                              f"你已清空所有绑定设备！")
