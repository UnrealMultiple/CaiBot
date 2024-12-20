import datetime

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from common.group import Group
from common.user import User, LoginRequest


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


login = on_command('登录', aliases={"批准", "允许", "登陆"}, force_whitespace=True)


@login.handle()
async def login_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await login.finish(MessageSegment.at(event.user_id) +
                           f'\n『登录系统』\n' +
                           "你还没有添加白名单！\n"
                           f"发送'添加白名单 <名字>'来添加白名单")
    if user.login_request.time == datetime.datetime.min:
        await login.finish(MessageSegment.at(event.user_id) +
                           f"\n『登录系统』\n"
                           f"你目前没有收到任何登录请求！")
    if not is_within_5_minutes(user.login_request.time):
        await login.finish(MessageSegment.at(event.user_id) +
                           f"\n『登录系统』\n"
                           f"登录请求已失效！")
    user.uuid.append(user.login_request.uuid)
    if len(user.uuid) >5:
        user.uuid.pop(0)
    user.login_request = LoginRequest(datetime.datetime.min, "")
    user.update()
    await login.finish(MessageSegment.at(event.user_id) +
                       f"\n『登录系统』\n"
                       f"✅已接受此登录请求！\n"
                       f"使用'清空设备'解除所有绑定")


reject_login = on_command('拒绝', aliases={"不批准", "不允许"}, force_whitespace=True)


@reject_login.handle()
async def reject_login_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await reject_login.finish(MessageSegment.at(event.user_id) +
                                  f'\n『登录系统』\n' +
                                  "你还没有添加白名单！\n"
                                  f"发送'添加白名单 <名字>'来添加白名单")
    if user.login_request.time == datetime.datetime.min:
        await reject_login.finish(MessageSegment.at(event.user_id) +
                                  f"\n『登录系统』\n"
                                  f"你目前没有收到任何登录请求！")
    if not is_within_5_minutes(user.login_request.time):
        await reject_login.finish(MessageSegment.at(event.user_id) +
                                  f"\n『登录系统』\n"
                                  f"登录请求已失效！")
    user.login_request = LoginRequest(datetime.datetime.min, "")
    user.update()
    await reject_login.finish(MessageSegment.at(event.user_id) +
                              f"\n『登录系统』\n"
                              f"❌已拒绝此批准！")


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
