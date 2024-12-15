import html

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from common.group import Group
from common.group_helper import GroupHelper
from common.user import User
from plugins.cai_api import wait_for_online, server_connection_manager


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

remote_command = on_command("#", aliases={"远程命令", "远程指令", "c"}, force_whitespace=True)


@remote_command.handle()
async def remote_command_handle(event: GroupMessageEvent):
    msg = GroupHelper.at_to_name(html.unescape(event.raw_message)).split(" ", 2)
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 3 or msg[2] == "":
            await remote_command.finish(MessageSegment.at(event.user_id) +
                                        f'\n『远程指令』\n' +
                                        f"格式错误!正确格式: 远程指令 <服务器序号> <命令内容>")
        if msg[2][0] != "/":
            msg[2] = "/" + msg[2]
        cmd = {
            "type": "cmd",
            "cmd": msg[2],
            "at": str(event.user_id)
        }
        if len(group.servers) == 0:
            await remote_command.finish(MessageSegment.at(event.user_id) +
                                        f'\n『远程指令』\n' +
                                        f"你好像还没有绑定服务器捏？")
        if msg[1] == "all" or msg[1] == "*":
            id = 0
            for i in group.servers:
                id += 1
                if not server_connection_manager.server_available(i.token):
                    await remote_command.send(MessageSegment.at(event.user_id) +
                                              f'\n『远程指令』\n' +
                                              f"执行失败！\n"
                                              f"❌服务器[{id}]处于离线状态")
                else:
                    await server_connection_manager.send_data(i.token, cmd, event.group_id)
            return
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await remote_command.finish(MessageSegment.at(event.user_id) +
                                        f'\n『远程指令』\n' +
                                        f"执行失败！\n"
                                        f"服务器序号错误!")
        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await remote_command.finish(MessageSegment.at(event.user_id) +
                                        f'\n『远程指令』\n' +
                                        f"执行失败！\n"
                                        f"❌服务器[{int(msg[1])}]处于离线状态")
        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await remote_command.finish(MessageSegment.at(event.user_id) +
                                    f'\n『远程指令』\n' +
                                    "没有权限!")


online = on_command("在线", aliases={"在线人数", "在线查询", "泰拉在线", "查询在线"}, force_whitespace=True)


@online.handle()
async def remote_command_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    if len(group.servers) == 0:
        await online.finish(MessageSegment.at(event.user_id) +
                            f'\n『泰拉在线』\n' +
                            f"你好像还没有绑定服务器捏？")
    result = await wait_for_online(event.group_id, group.servers)

    await online.finish(MessageSegment.at(event.user_id) +
                        f'\n『泰拉在线』\n' +
                        "\n".join(result))


world_progress = on_command("进度", aliases={"进度查询", "查询进度"}, force_whitespace=True)


@world_progress.handle()
async def world_progress_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    msg = msg_cut(event.get_plaintext())
    if len(msg) == 2:
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await world_progress.finish(MessageSegment.at(event.user_id) +
                                        f'\n『进度查询』\n' +
                                        f"获取失败！\n"
                                        f"服务器序号错误!")
        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await world_progress.finish(MessageSegment.at(event.user_id) +
                                        f'\n『进度查询』\n' +
                                        f"执行失败！\n"
                                        f"❌服务器[{int(msg[1])}]处于离线状态")
        cmd = {
            "type": "process"
        }
        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await world_progress.finish(MessageSegment.at(event.user_id) +
                                    f'\n『进度查询』\n'
                                    f'查询失败！\n'
                                    f'格式错误！正确格式: 进度查询 [服务器序号]')


self_kick = on_command("自踢", aliases={"自提", "自体"}, force_whitespace=True)


@self_kick.handle()
async def self_kick_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    user = User.get_user(event.user_id)
    if user is None:
        await self_kick.finish(MessageSegment.at(event.user_id) +
                               f'\n『自踢』\n' +
                               "你还没有添加白名单！\n"
                               f"发送'添加白名单 <名字>'来添加白名单")
    cmd = {
        "type": "selfkick",
        "name": user.name
    }
    for i in group.servers:
        await server_connection_manager.send_data(i.token, cmd, event.group_id)
    await self_kick.finish(MessageSegment.at(event.user_id) +
                           f'\n『自踢』\n' +
                           f"自踢成功！")


get_map_png = on_command("查看地图", force_whitespace=True)


@get_map_png.handle()
async def get_map_png_handle(event: GroupMessageEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_id)
    if not group.enable_server_bot:
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 2:
            await get_map_png.finish(MessageSegment.at(event.user_id) +
                                     f'\n『查看地图』\n' +
                                     f"格式错误!正确格式: 查看地图 <服务器序号>")
        cmd = {
            "type": "mappng"
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await get_map_png.finish(MessageSegment.at(event.user_id) +
                                     f'\n『查看地图』\n' +
                                     f"获取失败！\n"
                                     f"服务器序号错误!")

        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await get_map_png.finish(MessageSegment.at(event.user_id) +
                                     f'\n『查看地图』\n' +
                                     f"获取失败！\n"
                                     f"❌服务器[{int(msg[1])}]处于离线状态")
        try:
            server = server_connection_manager.get_server(group.servers[int(msg[1]) - 1].token)
            if server.terraria_version.startswith("tModLoader"):
                await get_map_png.finish(MessageSegment.at(event.user_id) +
                                         f'\n『查看地图』\n' +
                                         f"获取失败！\n"
                                         f"❌不支持tModLoader服务器")
        except:
            pass

        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await get_map_png.finish(MessageSegment.at(event.user_id) +
                                 f'\n『查看地图』\n' +
                                 "没有权限!")


get_world_file = on_command("下载地图", force_whitespace=True)


@get_world_file.handle()
async def get_world_file_handle(event: GroupMessageEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_id)
    if not group.enable_server_bot:
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 2:
            await get_world_file.finish(MessageSegment.at(event.user_id) +
                                        f'\n『下载地图』\n' +
                                        f"格式错误!正确格式: 下载地图 <服务器序号>")
        cmd = {
            "type": "worldfile"
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await get_world_file.finish(MessageSegment.at(event.user_id) +
                                        f'\n『下载地图』\n' +
                                        f"获取失败！\n"
                                        f"服务器序号错误!")
        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await get_world_file.finish(MessageSegment.at(event.user_id) +
                                        f'\n『下载地图』\n' +
                                        f"获取失败！\n"
                                        f"❌服务器[{int(msg[1])}]处于离线状态")
        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await get_world_file.finish(MessageSegment.at(event.user_id) +
                                    f'\n『下载地图』\n' +
                                    "没有权限!")


get_map_file = on_command("下载小地图", force_whitespace=True)


@get_map_file.handle()
async def get_world_file_handle(event: GroupMessageEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_id)
    if not group.enable_server_bot:
        return
    if await GroupHelper.HasPermission(event.group_id, event.user_id):
        if len(msg) != 2:
            await get_map_file.finish(MessageSegment.at(event.user_id) +
                                      f'\n『下载小地图』\n' +
                                      f"格式错误!正确格式: 下载小地图 <服务器序号>")
        cmd = {
            "type": "mapfile"
        }
        if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
            await get_map_file.finish(MessageSegment.at(event.user_id) +
                                      f'\n『下载小地图』\n' +
                                      f"获取失败！\n"
                                      f"服务器序号错误!")
        if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
            await get_map_file.finish(MessageSegment.at(event.user_id) +
                                      f'\n『下载小地图』\n' +
                                      f"获取失败！\n"
                                      f"❌服务器[{int(msg[1])}]处于离线状态")
        await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)
    else:
        await get_map_file.finish(MessageSegment.at(event.user_id) +
                                  f'\n『下载小地图』\n' +
                                  "没有权限!")


get_plugin_list = on_command("插件列表", aliases={"模组列表"}, force_whitespace=True)


@get_plugin_list.handle()
async def get_plugin_list_handle(event: GroupMessageEvent):
    msg = msg_cut(event.get_plaintext())
    group = Group.get_group(event.group_id)
    if not group.enable_server_bot:
        return
    if len(msg) != 2:
        await get_plugin_list.finish(MessageSegment.at(event.user_id) +
                                     f'\n『插件列表』\n' +
                                     f"格式错误!正确格式: 插件列表 <服务器序号>")
    cmd = {
        "type": "pluginlist"
    }
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await get_plugin_list.finish(MessageSegment.at(event.user_id) +
                                     f'\n『插件列表』\n' +
                                     f"获取失败！\n"
                                     f"服务器序号错误!")
    if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
        await get_plugin_list.finish(MessageSegment.at(event.user_id) +
                                     f'\n『插件列表』\n' +
                                     f"获取失败！\n"
                                     f"❌服务器[{int(msg[1])}]处于离线状态")
    await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)


look_bag = on_command("查背包", aliases={"查看背包", "查询背包"}, force_whitespace=True)


@look_bag.handle()
async def look_bag_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    msg = msg_cut(GroupHelper.at_to_name(event.raw_message))
    if not group.enable_server_bot:
        return

    if len(msg) != 3:
        await look_bag.finish(MessageSegment.at(event.user_id) +
                              f'\n『查背包』\n' +
                              f"格式错误!正确格式: 查背包 <服务器序号> <玩家名>")
    cmd = {
        "type": "lookbag",
        "name": msg[2],
    }
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await look_bag.finish(MessageSegment.at(event.user_id) +
                              f'\n『查背包』\n' +
                              f"查询失败！\n"
                              f"服务器序号错误!")
    if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
        await look_bag.finish(MessageSegment.at(event.user_id) +
                              f'\n『查背包』\n' +
                              f"查询失败！\n"
                              f"❌服务器[{int(msg[1])}]处于离线状态")
    await server_connection_manager.send_data(group.servers[int(msg[1]) - 1].token, cmd, event.group_id)


server_list = on_command("服务器列表", aliases={"ip", "IP"}, force_whitespace=True)


@server_list.handle()
async def server_list_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    result = []
    id = 1
    for i in group.servers:
        if server_connection_manager.server_available(i.token):
            # 『服务器列表』
            # ๑1๑cai的喵窝(v1.4.4.9)
            try:
                server = server_connection_manager.get_server(i.token)
                server_version = server.terraria_version
                world = server.world
                if server.whitelist:
                    white_list = "[Cai白名单]"
                else:
                    white_list = ""
                result.append(f"๑{id}๑🌐{world}{white_list}({server_version})\n地址：{i.ip}\n端口：{i.port}")
            except:
                result.append(f"๑{id}๑🌐请更新CaiBOT插件哦~\n地址：{i.ip}\n端口：{i.port}")

        else:
            result.append(f"๑{id}๑❌服务器处于离线状态")
        id += 1
    await server_list.finish(MessageSegment.at(event.user_id) +
                             f'\n『泰拉在线』\n' +
                             "\n".join(result))


server_info = on_command("服务器信息", force_whitespace=True)


@server_info.handle()
async def server_info_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    msg = msg_cut(event.get_plaintext())
    if not group.enable_server_bot:
        return

    if len(msg) != 2:
        await server_info.finish(MessageSegment.at(event.user_id) +
                                 f'\n『服务器信息』\n' +
                                 f"格式错误!正确格式: 服务器信息 <服务器序号>")
    if not msg[1].isdigit() or int(msg[1]) > len(group.servers):
        await server_info.finish(MessageSegment.at(event.user_id) +
                                 f'\n『服务器信息』\n' +
                                 f"查询失败！\n"
                                 f"服务器序号错误!")
    if not server_connection_manager.server_available(group.servers[int(msg[1]) - 1].token):
        await server_info.finish(MessageSegment.at(event.user_id) +
                                 f'\n『服务器信息』\n' +
                                 f"查询失败！\n"
                                 f"❌服务器[{int(msg[1])}]处于离线状态")
    i = group.servers[int(msg[1]) - 1]
    try:
        # "tshock_version":"5.2.0.0","plugin_version":"2024.6.7.0","terraria_version":"v1.4.4.9","whitelist":false,"os":"win10-x64"
        server = server_connection_manager.get_server(i.token)
        server_version = server.terraria_version
        world = server.world
        tshock_version = server.tshock_version
        whitelist = server.whitelist
        plugin_version = server.plugin_version
        os = server.os
        await server_info.send(MessageSegment.at(event.user_id) +
                               f'\n『服务器信息』\n' +
                               f"服务器[{int(msg[1])}]的详细信息: \n"
                               f"地址: {i.ip}:{i.port}\n"
                               f"世界名: {world}\n"
                               f"Terraria版本: {server_version}\n"
                               f"TShock版本: {tshock_version}\n"
                               f"CaiBot扩展版本: {plugin_version}\n"
                               f"Cai白名单: {whitelist}\n"
                               f"服务器系统: {os}\n"
                               f"所属群: {i.owner}\n"
                               f"共享群: {'无' if not i.shared else ','.join(map(str, i.shared))}")
        return
    except:
        await server_info.finish(MessageSegment.at(event.user_id) +
                                 f'\n『服务器信息』\n' +
                                 f"服务器[{int(msg[1])}]的详细信息: \n"
                                 f"地址: {i.ip}:{i.port}\n"
                                 f"🌐详细信息获取失败,请更新CaiBOT插件哦~")
