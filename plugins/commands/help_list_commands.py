from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

from utils.group import Group

FEED_BACK_GROUP = 991556763


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


update = \
    """🧪适配插件下载: https://wwf.lanzouj.com/b0mahl2xg 密码:2pdn
🌐安装教程: https://tr.monika.love/resources/118/
"""

help_list = on_command("菜单", aliases={"帮助"}, force_whitespace=True)


@help_list.handle()
async def help_handle(event: GroupMessageEvent):
    await help_list.finish(MessageSegment.at(event.user_id) +
                           f'\n『菜单』\n'
                           f'⚡服务器管理\n'
                           f'⚡云黑菜单\n'
                           f'⚡快捷功能菜单\n'
                           f'⚡地图功能菜单\n'
                           f'⚡白名单菜单\n'
                           f'⚡图鉴搜索菜单\n\n'
                           + update)


ban_help = on_command("云黑帮助", aliases={"云黑菜单"}, force_whitespace=True)


@ban_help.handle()
async def ban_help_handle(event: GroupMessageEvent):
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


help1 = on_command("服务器管理", force_whitespace=True)


@help1.handle()
async def help1_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help1.finish(MessageSegment.at(event.user_id) +
                       f'\n『菜单•服务器管理』\n'
                       f'⚡添加服务器 <IP地址> <端口> <验证码>\n'
                       f'⚡删除服务器 <服务器序号> \n'
                       f'⚡共享服务器 <服务器序号> <群号>\n'
                       f'⚡取消共享服务器 <服务器序号> <群号>\n'
                       f'⚡服务器列表 [获取服务器地址端口等]\n'
                       f'⚡服务器信息 <服务器序号> [获取服务器详细信息]')


help2 = on_command("快捷功能菜单", force_whitespace=True)


@help2.handle()
async def help2_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help2.finish(MessageSegment.at(event.user_id) +
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


help3 = on_command("地图功能菜单", force_whitespace=True)


@help3.handle()
async def help3_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help3.finish(MessageSegment.at(event.user_id) +
                       f'\n『菜单•地图功能』\n'
                       f'⚡查看地图 <服务器序号> [获取地图图片]\n'
                       f'⚡下载地图  <服务器序号> [获取地图文件(可能不可用)]\n'
                       f'⚡下载小地图  <服务器序号> [获取点亮的小地图文件]')


help4 = on_command("白名单菜单", force_whitespace=True)


@help4.handle()
async def help4_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help4.finish(MessageSegment.at(event.user_id) +
                       f'\n『菜单•白名单』\n'
                       f'⚡签到 [没啥用]\n'
                       f'⚡查询金币 [字面意思]\n'
                       f'⚡添加白名单 <名字> [绑定角色]\n'
                       f'⚡修改白名单 <名字> [重新绑定角色]')


help5 = on_command("图鉴搜索菜单", force_whitespace=True)


@help5.handle()
async def help5_handle(event: GroupMessageEvent):
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    await help5.finish(MessageSegment.at(event.user_id) +
                       f'\n『菜单•图鉴搜索』\n'
                       f'⚡si <名字|ID> [搜物品]\n'
                       f'⚡sn <名字|ID> [搜生物]\n'
                       f'⚡sp <名字|ID> [搜弹幕]\n'
                       f'⚡sb <名字|ID> [搜Buff]\n'
                       f'⚡sx <名字|ID> [搜修饰语]')
