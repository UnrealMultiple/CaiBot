import re
import socket
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from common.group_helper import GroupHelper
from common.server_helper import ping_server
from common.statistics import Statistics
from plugins import cai_api


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


about = on_command("关于", force_whitespace=True)


@about.handle()
async def ban_about_handle(event: GroupMessageEvent):
    statistics = Statistics.get_statistics()
    await about.finish(MessageSegment.at(event.user_id) +
                       f'\n『关于』\n'
                       f'📖小小Cai\n'
                       f'🎉开发者: Cai(3042538328)\n'
                       f'✨贡献者: \n'
                       f'迅猛龙(3407905827) [提供服务器]\n'
                       f'羽学(1242509682) [代码贡献]\n'
                       f'2409:(1651309670) [代码贡献]\n'
                       f'西江(3082068984) [代码贡献]\n'
                       f'🌐反馈群: 991556763\n'
                       f'⚡小小Cai已加入{statistics.total_group}个群,已记录{statistics.total_ban}名云黑用户\n'
                       f'入群检测{statistics.total_check}次,拒绝了{statistics.total_kick}次入群请求\n'
                       f'绑定{statistics.total_users}名玩家,检查白名单{statistics.check_whitelist}次\n'
                       f'绑定{statistics.total_servers}台服务器,当前已连接{len(cai_api.server_connection_manager.connections)}台\n'
                       f'Powered by Nonebot2 & LLOneBot')


def version_key(version):
    return [int(part) if part.isdigit() else part for part in re.split('(\d+)', version)]


server_statistics = on_command("CaiBot统计", force_whitespace=True)


@server_statistics.handle()
async def plugin_version_handle(event: GroupMessageEvent):
    version_count = {}
    tshock_count = {}
    os_count = {}
    whitelist_count = 0
    for server in cai_api.server_connection_manager.connections.values():
        version = server.plugin_version
        if version in version_count:
            version_count[version] += 1
        else:
            version_count[version] = 1

        tshock_version = server.tshock_version
        if tshock_version in tshock_count:
            tshock_count[tshock_version] += 1
        else:
            tshock_count[tshock_version] = 1

        if server.whitelist:
            whitelist_count += 1

        os = server.os
        if os in os_count:
            os_count[os] += 1
        else:
            os_count[os] = 1

    sorted_versions = sorted(version_count.items(), key=lambda item: version_key(item[0]), reverse=True)
    tshock_sorted_versions = sorted(tshock_count.items())
    tshock_info = "\n".join([f"v{version} > {count}" for version, count in tshock_sorted_versions])
    version_info = "\n".join([f"v{version} > {count}" for version, count in sorted_versions])
    os_info = "\n".join([f"{os} > {count}" for os, count in os_count.items()])
    await server_statistics.finish(MessageSegment.at(event.user_id) +
                                   f'\n『CaiBot统计』\n'
                                   f'🔭适配插件版本:\n'
                                   f'{version_info}\n'
                                   f'#⃣TShock版本:\n'
                                   f'{tshock_info}\n'
                                   f'✨系统版本:\n'
                                   f'{os_info}\n'
                                   f'📖白名单服务器:\n'
                                   f'{whitelist_count}台')


broadcast = on_command("群发消息", force_whitespace=True)


@broadcast.handle()
async def broadcast_handle(event: GroupMessageEvent):
    if event.user_id == 3042538328:
        msg = event.get_plaintext().split(" ", 1)
        msg = msg[1]
        await GroupHelper.send_all_groups(msg)


lookfor = on_command("lookfor", force_whitespace=True)


@lookfor.handle()
async def lookfor_handle(event: GroupMessageEvent):
    if event.user_id != 3042538328:
        await lookfor.finish(MessageSegment.at(event.user_id) +
                             f'\n『LookFor』\n'
                             + "没有权限")
    msg = msg_cut(GroupHelper.at_to_name(event.raw_message))
    if len(msg) != 2:
        await lookfor.finish(MessageSegment.at(event.user_id) +
                             f'\n『LookFor』\n'
                             + "格式错误!正确格式: LookFor <QQ号>")
    else:
        try:
            qq_num = int(msg[1])
        except ValueError:
            await lookfor.finish(MessageSegment.at(event.user_id) +
                                 f'\n『LookFor』\n'
                                 + "格式错误!无效QQ号")
        result = await GroupHelper.look_for_from_groups(qq_num)
        lines = []
        for i in result:
            lines.append(f"{i[0]}({i[1]})")
        if len(lines) == 0:
            await lookfor.finish(MessageSegment.at(event.user_id) +
                                 f'\n『LookFor』\n'
                                 + f"[{qq_num}]不在小小Cai加入的任何群中")
        else:
            await lookfor.finish(MessageSegment.at(event.user_id) +
                                 f'\n『LookFor』\n'
                                 + f"[{qq_num}]的查询结果:\n"
                                 + "\n".join(lines))


ping = on_command("ping", force_whitespace=True)


@ping.handle()
async def ping_handle(event: GroupMessageEvent):
    msg = msg_cut(event.get_plaintext())
    if len(msg) != 3:
        await ping.finish(MessageSegment.at(event.user_id) +
                          f'\n『PING』\n' +
                          f"格式错误!正确格式: ping <服务器地址> <端口>")
    try:
        adr = socket.gethostbyname(msg[1])
    except:
        await ping.finish(MessageSegment.at(event.user_id) +
                          f'\n『PING』\n' +
                          f"没有找到服务器欸？")

    try:
        time, packId = await ping_server(adr, int(msg[2]))
    except TimeoutError:
        await ping.finish(MessageSegment.at(event.user_id) +
                          f'\n『PING』\n' +
                          f"服务器连接超时！")
    except Exception as ex:
        await ping.finish(MessageSegment.at(event.user_id) +
                          f'\n『PING』\n' +
                          f"连接失败！\n错误：{str(ex)}")
    packId = str(packId)
    if packId == "2":
        await ping.finish(MessageSegment.at(event.user_id) +
                          f'\n『PING』\n' +
                          f"PING到服务器啦!\n"
                          f"延迟: {time:.2f}ms, 响应数据包：{packId}\n"
                          f"然后小小Cai被服务器一脚踢了出去，呜呜呜...")
    if packId != "LegacyMultiplayer4" and packId != "3":
        await ping.finish(MessageSegment.at(event.user_id) +
                          f'\n『PING』\n' +
                          f"PING到服务器啦!\n"
                          f"延迟: {time:.2f}ms, 响应数据包：{packId}\n"
                          f"但是小小Cai发现这好像不是Terraria服务器？")
    await ping.finish(MessageSegment.at(event.user_id) +
                      f'\n『PING』\n' +
                      f"PING到服务器啦!\n"
                      f"延迟: {time:.2f}ms, 响应数据包：{packId}")
