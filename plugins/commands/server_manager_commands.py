import uuid

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from common.group import Group
from common.group_helper import GroupHelper
from common.server import Server
from plugins import cai_api
from plugins.cai_api import server_connection_manager


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


add_server = on_command("添加服务器", force_whitespace=True)


@add_server.handle()
async def add_server_handle(event: GroupMessageEvent):
    if not await GroupHelper.HasPermission(event.group_id, event.user_id):
        await add_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『添加服务器』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")
    group = Group.get_group(event.group_id)
    if group is None:
        await add_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『添加服务器』\n' +
                                "请先加入云黑!\n" +
                                "群内发送'启用云黑'")
    if not group.enable_server_bot:
        await add_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『添加服务器』\n' +
                                "请启用群机器人!" +
                                "群内发送'启用群机器人'")
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 4:
        await add_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『添加服务器』\n' +
                                f"格式错误!正确格式: 添加服务器 <IP地址> <端口> <验证码> [需要服务器适配插件]")
    # try:
    #     res = await set_server(msg[1], int(msg[2]), int(msg[3]))
    # except:
    cai_api.add_token(int(msg[3]), Server(str(uuid.uuid4()), event.group_id, [], msg[1], int(msg[2])), 300)
    await add_server.finish(MessageSegment.at(event.user_id) +
                            f'\n『添加服务器』\n' +
                            f"正在绑定服务器中...\n"
                            f"请确保你的服务器绑定码为: {int(msg[3])}")
    # if res is None:
    #     await add_server.finish(MessageSegment.at(event.user_id) +
    #                             f'\n『添加服务器』\n' +
    #                             f"目标服务器没有添加机器人适配插件")
    # elif res == 'exist':
    #     await add_server.finish(MessageSegment.at(event.user_id) +
    #                             f'\n『添加服务器』\n' +
    #                             f"绑定失败！\n此服务器已被绑定！")
    # elif res == 'code':
    #     await add_server.finish(MessageSegment.at(event.user_id) +
    #                             f'\n『添加服务器』\n' +
    #                             f"验证码错误！")
    # else:
    #     pattern = r'^\{?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}?$'
    #     match = re.match(pattern, res)
    #     if not bool(match):
    #         await add_server.finish(MessageSegment.at(event.user_id) +
    #                                 f'\n『添加服务器』\n' +
    #                                 f"绑定失败！\n服务器绑定无效，请重试！")
    #     # group.servers.append(Server(res, event.group_id, [], msg[1], int(msg[2])))
    #     Server.add_server(res, event.group_id, msg[1], int(msg[2]))
    #     await add_server.finish(MessageSegment.at(event.user_id) +
    #                             f'\n『添加服务器』\n' +
    #                             f"服务器绑定成功")

edit_server = on_command("修改服务器", force_whitespace=True)


@edit_server.handle()
async def edit_server_handle(event: GroupMessageEvent):
    if not await GroupHelper.HasPermission(event.group_id, event.user_id):
        await edit_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『修改服务器』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")
    group = Group.get_group(event.group_id)
    if group is None:
        await edit_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『修改服务器』\n' +
                                "请先加入云黑!\n" +
                                "群内发送'启用云黑'")
    if not group.enable_server_bot:
        await edit_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『修改服务器\n' +
                                "请启用群机器人!" +
                                "群内发送'启用群机器人'")
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 4:
        await edit_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『修改服务器』\n' +
                                f"格式错误!正确格式: 修改服务器 <服务器序号> <新IP地址> <新端口>")
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await edit_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『修改服务器』\n'
                                  f"服务器序号错误!")
    index = int(msg[1]) - 1
    group.servers[index].ip = int(msg[2])
    group.servers[index].port = int(msg[3])
    group.servers[index].update()
    await edit_server.finish(MessageSegment.at(event.user_id) +
                              f'\n『修改服务器』\n'
                              f"修改成功!\n"
                              f"服务器IP信息已改为: {group.servers[index].ip}:{group.servers[index].port}~")


share_server = on_command("共享服务器", force_whitespace=True)


@share_server.handle()
async def share_server_handle(event: GroupMessageEvent):
    if not await GroupHelper.is_owner(event.group_id, event.user_id):
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n' +
                                  "没有权限!\n"
                                  "只允许群主设置")
    group = Group.get_group(event.group_id)
    if group is None:
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n' +
                                  "请先加入云黑!\n" +
                                  "群内发送'启用云黑'")
    if not group.enable_server_bot:
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n' +
                                  "请启用群机器人!" +
                                  "群内发送'启用群机器人'")
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 3:
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n' +
                                  f"格式错误!正确格式: 共享服务器 <服务器序号> <共享服务器群号>")
    if not msg[2].isdigit():
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n'
                                  + f"QQ群号格式错误!")
    if int(msg[2]) == event.group_id:
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n'
                                  f'Cai向Cai分享了Cai的Cai服务器\n'
                                  f'这合理吗?')
    if not await GroupHelper.is_admin(int(msg[2]), event.user_id):
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n'
                                  f'没有权限哦~\n'
                                  f"你必须是群[{msg[2]}]的管理员或群主!")
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n'
                                  f"服务器序号错误!")
    if not group.servers[int(msg[1]) - 1].is_owner_server(event.group_id):
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n'
                                  f"只能由服务器拥有群[{group.servers[int(msg[1]) - 1].owner}]发起共享!")
    if int(msg[2]) in group.servers[int(msg[1]) - 1].shared:
        await share_server.finish(MessageSegment.at(event.user_id) +
                                  f'\n『共享服务器』\n'
                                  f"本群已被共享过此服务器!")
    group.servers[int(msg[1]) - 1].shared.append(int(msg[2]))
    group.servers[int(msg[1]) - 1].update()
    await server_connection_manager.disconnect(group.servers[int(msg[1]) - 1].token)
    await share_server.finish(MessageSegment.at(event.user_id) +
                              f'\n『共享服务器』\n'
                              f"共享成功!\n"
                              f"你可以使用'取消共享服务器'来取消对目标群的服务器共享哦~")


unshare_server = on_command("取消共享服务器", force_whitespace=True)


@unshare_server.handle()
async def unshare_server_handle(event: GroupMessageEvent):
    if not await GroupHelper.HasPermission(event.group_id, event.user_id):
        await unshare_server.finish(MessageSegment.at(event.user_id) +
                                    f'\n『共享服务器』\n' +
                                    "没有权限!\n"
                                    "只允许群主和管理员设置")
    group = Group.get_group(event.group_id)
    if group is None:
        await unshare_server.finish(MessageSegment.at(event.user_id) +
                                    f'\n『共享服务器』\n' +
                                    "请先加入云黑!\n" +
                                    "群内发送'启用云黑'")
    if not group.enable_server_bot:
        await unshare_server.finish(MessageSegment.at(event.user_id) +
                                    f'\n『共享服务器』\n' +
                                    "请启用群机器人!" +
                                    "群内发送'启用群机器人'")
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 3:
        await unshare_server.finish(MessageSegment.at(event.user_id) +
                                    f'\n『共享服务器』\n' +
                                    f"格式错误!正确格式: 取消共享服务器 <服务器序号> <共享服务器群号>")
    if not msg[2].isdigit():
        await unshare_server.finish(MessageSegment.at(event.user_id) +
                                    f'\n『共享服务器』\n'
                                    + f"QQ群号格式错误!")
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await unshare_server.finish(MessageSegment.at(event.user_id) +
                                    f'\n『共享服务器』\n'
                                    f"服务器序号错误!")
    if not group.servers[int(msg[1]) - 1].is_owner_server(event.group_id):
        await unshare_server.finish(MessageSegment.at(event.user_id) +
                                    f'\n『共享服务器』\n'
                                    f"只能由服务器拥有群[{group.servers[int(msg[1]) - 1].owner}]才能取消共享!")
    if not int(msg[2]) in group.servers[int(msg[1]) - 1].shared:
        await unshare_server.finish(MessageSegment.at(event.user_id) +
                                    f'\n『共享服务器』\n'
                                    f"本群没有被共享过此服务器!")
    group.servers[int(msg[1]) - 1].shared.remove(int(msg[2]))
    group.servers[int(msg[1]) - 1].update()
    await server_connection_manager.disconnect(group.servers[int(msg[1]) - 1].token)
    await unshare_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『共享服务器』\n'
                                f"取消共享成功!\n")


del_server = on_command("删除服务器", force_whitespace=True)


@del_server.handle()
async def del_server_handle(event: GroupMessageEvent):
    if not await GroupHelper.HasPermission(event.group_id, event.user_id):
        await del_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                "没有权限!\n"
                                "只允许群主和管理员设置")
    group = Group.get_group(event.group_id)
    if group is None:
        await del_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                "请先加入云黑!\n" +
                                "群内发送'启用云黑'")
    if not group.enable_server_bot:
        await del_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                "请启用群机器人!" +
                                "群内发送'启用群机器人'")
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 2:
        await del_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                f"格式错误!正确格式: 删除服务器 <服务器序号>")
    cmd = {
        "type": "delserver",
    }
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await del_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                f"删除失败！\n"
                                f"服务器序号错误!")
    if group.servers[int(msg[1]) - 1].is_owner_server(event.group_id):
        if server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
        Server.del_server(group.servers[int(msg[1]) - 1].token)
        await server_connection_manager.disconnect(group.servers[int(msg[1]) - 1].token)
        del group.servers[int(msg[1]) - 1]
        await del_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                f"服务器删除成功!\n"
                                f"若解绑失败，请删除服务器tshock/CaiBot.json然后重启")
    else:
        group.servers[int(msg[1]) - 1].shared.remove(group.id)
        group.servers[int(msg[1]) - 1].update()
        await server_connection_manager.disconnect(group.servers[int(msg[1]) - 1].token)
        await del_server.finish(MessageSegment.at(event.user_id) +
                                f'\n『删除服务器』\n' +
                                f"服务器已被取消共享!")
