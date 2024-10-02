import asyncio
import base64
import datetime
import gzip
import io
import json
import os
import threading
import time
import zipfile

import aiohttp
import nonebot
import requests
import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException, Request
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from starlette.websockets import WebSocketDisconnect

import config
import plugins.event_handle
from plugins.event_handle import TSHOCK_GROUP
from utils import statistics
from utils.bag_png_helper import get_bag_png
from utils.ban_user import UserBan
from utils.group import Group
from utils.group_helper import GroupHelper
from utils.process_png_helper import get_process_png
from utils.server import Server
from utils.text_handle import TextHandle
from utils.user import User, LoginRequest


# TEST

def decompress_base64_gzip(base64_string):
    # 将Base64字符串解码为字节
    compressed_data = base64.b64decode(base64_string)

    # 使用GZip解压缩字节数据
    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gzip_file:
        decompressed_data = gzip_file.read()

    return decompressed_data.decode('utf-8')


async def download_and_upload():
    file_data = await nonebot.get_bot().call_api("get_group_root_files", group_id=TSHOCK_GROUP)
    files = [i for i in file_data['files'] if i['uploader'] == 2990574917]
    files.sort(key=lambda x: x['modify_time'], reverse=True)
    if len(files) >= 10:
        files_to_delete = files[9:]
        for file in files_to_delete:
            await nonebot.get_bot().call_api("delete_group_file", group_id=TSHOCK_GROUP,
                                             file_id=file['file_id'], busid=file['busid'])

    for file in files:
        if file['file_name'] == f"(v{datetime.datetime.now().strftime('%Y.%m.%d')})Plugins.zip":
            await nonebot.get_bot().call_api("delete_group_file", group_id=TSHOCK_GROUP,
                                             file_id=file['file_id'], busid=file['busid'])

    async with aiohttp.ClientSession() as session:
        async with session.get(
                "https://gitee.com/kksjsj/TShockPlugin/releases/download/V1.0.0.0/Plugins.zip") as response:
            file_data = await response.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
    await nonebot.get_bot().call_api("upload_group_file", group_id=TSHOCK_GROUP,
                                     file=f"base64://{base64_data}",
                                     name=f"(v{datetime.datetime.now().strftime('%Y.%m.%d')})Plugins.zip")
    print("插件包已推送！")


app = FastAPI()

star_user = []


@app.post("/plugins/github/")
async def handle_github_push(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")
    cst = datetime.timezone(datetime.timedelta(hours=8))  # 定义 CST 时区
    current_time = datetime.datetime.now(cst).strftime('%H:%M:%S')
    if event_type == "push":
        if "refs/tags/" in payload['ref']:
            return {"message": "阻止Tag推送..."}
        if payload['head_commit'] is None:
            return {"message": "阻止空提交推送..."}
        commits_message = ""
        for i in payload['commits']:
            commits_message += f"#️⃣ ({i['id'][:7]}) {i['message']} (by {i['author']['username']})\n"
        push_message = (f"⬆️ 新提交 {payload['repository']['full_name']} [{payload['ref'].split('/')[-1]}]\n"
                        f"by {payload['head_commit']['author']['name']}({payload['head_commit']['author']['username']}) | CST {current_time}\n\n"
                        f"{commits_message}\n"
                        f"查看差异 > {payload['compare']}")
        if payload['repository']['name'] == "TShockPlugin":
            await GroupHelper.send_group(plugins.event_handle.TSHOCK_GROUP, push_message)
        if payload['repository']['name'] == "CaiBot" and {payload['ref'].split('/')[-1]} == "master":
            await GroupHelper.send_group(plugins.event_handle.FEEDBACK_GROUP, push_message + "\n✨已发起自动更新...")
            url = 'https://github.com/UnrealMultiple/CaiBot/archive/refs/heads/master.zip'
            headers = {'Authorization': f'token {config.GITHUB_TOKEN}'}
            response = requests.get(url, headers=headers)
            # 获取当前运行目录
            current_dir = os.getcwd()

            # 解压并覆盖本地代码
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                for member in z.namelist():
                    # 去掉文件路径中的顶层文件夹
                    member_path = os.path.join(current_dir, os.path.relpath(member, start=z.namelist()[0]))
                    if member.endswith('/'):
                        os.makedirs(member_path, exist_ok=True)
                    else:
                        with z.open(member) as source, open(member_path, 'wb') as target:
                            target.write(source.read())
            await GroupHelper.send_group(plugins.event_handle.FEEDBACK_GROUP, "#️⃣代码下载完成, 需要手动重启")
        return {"message": "推送成功!"}
    if event_type == "ping":
        return {"message": "pong"}
    if event_type == "star":
        if payload['action'] == "created":
            if payload['sender']['login'] + payload['repository']['full_name'] not in star_user:
                star_user.append(payload['sender']['login'] + payload['repository']['full_name'])
                star_message = (
                    f"🔭 新Star {payload['repository']['full_name']} [{payload['repository']['default_branch']}]\n"
                    f"by {payload['sender']['login']} | CST {current_time}\n"
                    f"✨ 当前仓库共有{payload['repository']['stargazers_count']}颗星星")
                if payload['repository']['name'] == "TShockPlugin":
                    await GroupHelper.send_group(plugins.event_handle.TSHOCK_GROUP, star_message)
                if payload['repository']['name'] == "CaiBot":
                    await GroupHelper.send_group(plugins.event_handle.FEEDBACK_GROUP, star_message)
            return {"message": "推送成功！"}
    if event_type == "release":
        if payload['action'] == "edited":
            asyncio.create_task(download_and_upload())
            return {"message": "插件包正在推送，请稍候！"}
    if event_type == "pull_request":
        if payload['action'] == "opened":
            pull_message = (
                f"↙️ 新拉取请求 {payload['repository']['full_name']} [{payload['repository']['default_branch']}]\n"
                f"by {payload['pull_request']['user']['login']} | CST {current_time}\n\n"
                f"#️⃣ {payload['pull_request']['title']}\n\n"
                f"查看详细 > {payload['pull_request']['html_url']}")
            if payload['repository']['name'] == "TShockPlugin":
                await GroupHelper.send_group(plugins.event_handle.TSHOCK_GROUP, pull_message)
            if payload['repository']['name'] == "CaiBot":
                await GroupHelper.send_group(plugins.event_handle.FEEDBACK_GROUP, pull_message)
            return {"message": "推送成功!"}
    if event_type == "issues":
        if payload['action'] == "opened":
            issues_message = (
                f"❓ 新议题 {payload['repository']['full_name']} [{payload['repository']['default_branch']}]\n"
                f"by {payload['issue']['user']['login']} | CST {current_time}\n\n"
                f"#️⃣ {payload['issue']['title']}\n\n"
                f"查看详细 > {payload['issue']['html_url']}")
            if payload['repository']['name'] == "TShockPlugin":
                await GroupHelper.send_group(plugins.event_handle.TSHOCK_GROUP, issues_message)
            if payload['repository']['name'] == "CaiBot":
                await GroupHelper.send_group(plugins.event_handle.FEEDBACK_GROUP, issues_message)
            return {"message": "推送成功!"}
    return {"message": "未处理"}


tokens = {}


@app.get("/bot/get_token")
async def send_reset(code: int):
    current_time = datetime.datetime.now()
    if code in tokens:
        server, expiry_time = tokens[code]
        if current_time < expiry_time:
            server.add_self_server()
            tokens.pop(code)
            return {"status": 200, "token": server.token}
        else:
            tokens.pop(code)
            raise HTTPException(status_code=403, detail="token已失效!")
    else:
        raise HTTPException(status_code=403, detail="token获取失败!")


def add_token(code: int, server: Server, timeout: int):
    expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    tokens[code] = (server, expiry_time)


@app.post("/bot/send_reset")
async def send_reset(token: str, server_name: str, seed: str):
    server: Server = Server.get_server(token)
    if server is None:
        logger.warning(f"拒绝CaiAPI请求: {token},原因：不属于任何群的服务器")
        raise HTTPException(status_code=403,
                            detail="无效Token.")
    if await GroupHelper.is_bot_admin(server.owner):
        await GroupHelper.send_group(server.owner, MessageSegment.at("all") + f"\n『自动重置』\n"
                                                                              f"[{server_name}]已重置\n"
                                                                              f"种子: {seed}")
    else:
        await GroupHelper.send_group(server.owner, f"『自动重置』\n"
                                                   f"[{server_name}]已重置\n"
                                                   f"种子: {seed}")

    for i in server.shared:
        if await GroupHelper.is_bot_admin(server.owner):
            await GroupHelper.send_group(i, MessageSegment.at("all") + f"\n『自动重置』\n"
                                                                       f"[{server_name}]已重置\n"
                                                                       f"种子: {seed}")
        else:
            await GroupHelper.send_group(i, f"『自动重置』\n"
                                            f"[{server_name}]已重置\n"
                                            f"种子: {seed}")
    return {"status": 200}


websocket_connections: {str, WebSocket} = {}

last_connection_time = {}


@app.websocket("/bot/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    websocket_connections[token] = websocket
    try:
        server = Server.get_server(token)
        if server is None:
            cmd = {
                "type": "delserver",
                "group": 114514
            }
            await websocket.send_text(json.dumps(cmd))
            await websocket.close()
            if token in websocket_connections:
                del websocket_connections[token]
            logger.warning(f"服务器断开连接: {token},原因：不属于任何群的服务器")
            return
        group = Group.get_group_through_server(server)
        await websocket.send_text('{"type":"hello","group":' + str(group.id) + '}')
        logger.warning(f"群服务器已连接:{group.id}({token})")
        while True:
            if not server_available(token):
                await websocket.close(4002, f"CaiBot主动断开连接")
                break
            data = await websocket.receive_text()
            try:
                await handle_message(data, group, token, server, websocket)
            except Exception as ex:
                logger.warning(f"群服务器{group.id}({token}):{ex}")
    except WebSocketDisconnect as e:
        # 连接关闭时移除WebSocket连接
        if token in websocket_connections:
            del websocket_connections[token]
            logger.warning(f"服务器断开连接: {token},原因：{str(e)}")


online_request = {str: object}


async def wait_for_online(group_id: int, servers: list[Server]) -> [str]:
    cmd = {
        "type": "online"
    }
    result: [str] = []
    tasks = []
    for index, server in enumerate(servers):
        if server_available(server.token):
            if server.token in online_request:
                online_request.pop(server.token)
            task = asyncio.create_task(send_data(server.token, cmd, group_id))
            tasks.append(task)

    await asyncio.gather(*tasks)
    count = 0
    for index, server in enumerate(servers):
        if server_available(server.token):
            timeout = False
            while server.token not in online_request:
                if count == 200:
                    result.append(f"๑{index + 1}๑❌服务器连接超时")
                    timeout = True
                    break
                await asyncio.sleep(0.01)
                count += 1
            if not timeout:
                result.append(online_request.pop(server.token))
        else:
            result.append(f"๑{index + 1}๑❌服务器处于离线状态")
    return result


login_attempts = {}


# noinspection PyTypeChecker
async def handle_message(data: str, group: Group, token: str, server: Server, websocket) -> None:
    data = json.loads(data)
    if 'group' in data:
        if data['group'] != server.owner and data['group'] not in server.shared:
            return
        group = group.get_group(data['group'])
    index = server.get_server_index(group.id)
    if data['type'] != 'HeartBeat':
        logger.log(233, f"收到来自{group.id}({token})的数据: {data['type']}")
    if data['type'] == "cmd":
        if data['result']:
            await GroupHelper.send_group(group.id, MessageSegment.at(data['at']) + f"\n『远程指令』\n"
                                                                                   f"服务器[{index}]返回如下结果:\n" +
                                         f"{TextHandle.all(data['result'])}")
        else:
            await GroupHelper.send_group(group.id, f"『远程指令』\n"
                                                   f"服务器[{index}]返回了个寂寞")
    elif data['type'] == "online":
        result = f"๑{index}๑⚡{data['worldname']} 「{data['process']}」\n" + data['result']
        online_request[token] = result
    elif data['type'] == "process":
        progress_img = get_process_png(data)
        byte_arr = io.BytesIO()
        progress_img.save(byte_arr, format='PNG')
        byte_value = byte_arr.getvalue()
        await GroupHelper.send_group(group.id, message=MessageSegment.image(byte_value))
    elif data['type'] == "whitelist":
        user = User.get_user_name(data['name'])
        statistics.Statistics.add_check_whitelist()
        if user is None:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 404,
                "uuids": []
            }
            await send_data(token, re, None)
            return
        ban = UserBan.get_user(user.id)
        if ban is not None and len(ban.bans) > 1:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 403,
                "uuids": []
            }
            await send_data(token, re, None)
            return
        if ban is not None and ban.check_ban(user.id):
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 403,
                "uuids": []
            }
            await send_data(token, re, None)
            return
        member = False
        if await GroupHelper.is_member(group.id, user.id):
            member = True
        else:
            for i in server.shared:
                if await GroupHelper.is_member(i, user.id):
                    member = True
                    break
        if not member:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 401,
                "uuids": []
            }

            await send_data(token, re, None)
            return
        re = {
            "type": "whitelist",
            "name": data['name'],
            "code": 200,
            "uuids": user.uuid
        }
        await send_data(token, re, None)
    elif data['type'] == "device":
        # {"uuid", plr.UUID},
        # {"ip", plr.IP}
        # 获取当前时间
        current_time = time.time()
        ip = data['ip']
        name = data['name']
        uuid = data['uuid']
        user = User.get_user_name(name)
        if user is None:
            return
        if (ip not in login_attempts or current_time - login_attempts[ip] >= 120) or ip == "127.0.0.1":
            login_attempts[ip] = current_time
            addr = requests.get(f"https://whois.pconline.com.cn/ipJson.jsp?ip={ip}&json=true", timeout=5.0).json()[
                'addr']
            user.login_request = LoginRequest(datetime.datetime.now(), uuid)
            user.update()
            if await GroupHelper.is_member(server.owner, user.id):
                await GroupHelper.send_group(server.owner, message=MessageSegment.at(user.id) +
                                                                   f"\n『登录请求』\n" +
                                                                   f"有新的设备请求登录您的账号({addr.replace(' ', ',').replace('移通', '移动').lstrip(',')})\n" +
                                                                   f"✅回复'登录'允许登录\n" +
                                                                   f"❌回复'拒绝'拒绝登录")
                return
            for i in server.shared:
                if await GroupHelper.is_member(i, user.id):
                    await GroupHelper.send_group(i, message=MessageSegment.at(user.id) +
                                                            f"\n『登录请求』\n" +
                                                            f"有新的设备请求登录您的账号({addr.replace(' ', ',').replace('移通', '移动').lstrip(',')})\n" +
                                                            f"✅回复'登录'允许登录\n" +
                                                            f"❌回复'拒绝'拒绝登录")
                    return
    elif data['type'] == "mappng":
        base64_string = data['result']
        decoded_bytes = base64.b64decode(base64_string)
        await GroupHelper.send_group(group.id, message=MessageSegment.image(decoded_bytes))
    elif data['type'] == "mappngV2":
        base64_string = data['result']
        decoded_bytes = base64.b64decode(decompress_base64_gzip(base64_string))
        await GroupHelper.send_group(group.id, message=MessageSegment.image(decoded_bytes))
    elif data['type'] == "lookbag":
        if data['exist'] == 0:
            await GroupHelper.send_group(group.id, f"『查背包』\n" +
                                         f"查询失败!\n" +
                                         f"查询的玩家不存在！")
        else:
            img = get_bag_png(data['name'], data['inventory'], data['buffs'])
            byte_arr = io.BytesIO()
            img.save(byte_arr, format='PNG')
            byte_value = byte_arr.getvalue()
            await GroupHelper.send_group(group.id, message=MessageSegment.image(byte_value))
    elif data['type'] == "hello":
        # "tshock_version":"5.2.0.0","plugin_version":"2024.6.7.0","terraria_version":"v1.4.4.9","cai_whitelist":false,"os":"win10-x64"
        websocket.tshock_version = data['tshock_version']
        websocket.plugin_version = data['plugin_version']
        websocket.terraria_version = data['terraria_version']
        websocket.whitelist = data['cai_whitelist']
        websocket.world = data['world']
        websocket.os = data['os']
        plugins.API.websocket_connections[token] = websocket
        group_info = {
            "type": "groupid",
            "groupid": int(group.id)
        }
        logger.log(233, f"获取到{group.id}({token})的服务器信息: \n"
                        f"CaiBot版本: {data['plugin_version']}, TShock版本: {data['tshock_version']}, Cai白名单: {data['cai_whitelist']}, 系统:{data['os']}")
        await websocket.send_text(json.dumps(group_info))
    elif data['type'] == "worldfile":
        await nonebot.get_bot().call_api("upload_group_file", group_id=group.id, file=f"base64://{data['base64']}",
                                         name=data['name'])
        await GroupHelper.send_group(group.id, f"『下载地图』\n" +
                                     f"下载成功!\n" +
                                     f"PC导入路径: 文档/My Games/Terraria/Worlds\n"
                                     f"PE导入路径: Android/data/com.and.games505.TerrariaPaid/Worlds\n"
                                     f"*使用新版CaiBot插件可以大幅提高下载速度哦~")
    elif data['type'] == "worldfileV2":
        await nonebot.get_bot().call_api("upload_group_file", group_id=group.id,
                                         file=f"base64://{decompress_base64_gzip(data['base64'])}",
                                         name=data['name'])
        await GroupHelper.send_group(group.id, f"『下载地图』\n" +
                                     f"下载成功!\n" +
                                     f"PC导入路径: 文档/My Games/Terraria/Worlds\n"
                                     f"PE导入路径: Android/data/com.and.games505.TerrariaPaid/Worlds")
    elif data['type'] == "mapfile":
        await nonebot.get_bot().call_api("upload_group_file", group_id=group.id, file=f"base64://{data['base64']}",
                                         name=data['name'])
        await GroupHelper.send_group(group.id, f"『下载小地图』\n" +
                                     f"下载成功!\n" +
                                     f"PC导入路径: 文档/My Games/Terraria/Players/你的玩家名\n"
                                     f"PE导入路径: Android/data/com.and.games505.TerrariaPaid/Players/你的玩家名\n"
                                     f"请替换原来小地图文件，不要重命名!\n"
                                     f"*使用新版CaiBot插件可以大幅提高下载速度哦~")
    elif data['type'] == "mapfileV2":
        await nonebot.get_bot().call_api("upload_group_file", group_id=group.id,
                                         file=f"base64://{decompress_base64_gzip(data['base64'])}",
                                         name=data['name'])
        await GroupHelper.send_group(group.id, f"『下载小地图』\n" +
                                     f"下载成功!\n" +
                                     f"PC导入路径: 文档/My Games/Terraria/Players/你的玩家名\n"
                                     f"PE导入路径: Android/data/com.and.games505.TerrariaPaid/Players/你的玩家名\n"
                                     f"请替换原来小地图文件，不要重命名!")
    elif data['type'] == "pluginlist":
        update_check_result = ""
        has_new_version = False
        remote_plugins = requests.get("https://gitee.com/kksjsj/TShockPlugin/raw/master/Plugins.json").json()
        for local in data['plugins']:
            for remote in remote_plugins:
                if local["Name"] == remote["Name"]:
                    if list(map(int, local['Version'].split('.'))) < list(map(int, remote['Version'].split('.'))):
                        has_new_version = True
                        update_check_result += f"[{local['Name']}] v{local['Version']} >>> v{remote['Version']}\n"

        if has_new_version:
            await GroupHelper.send_group(group.id, f"『插件列表』\n" +
                                         "\n".join([f"{i['Name']} v{i['Version']} (by {i['Author']})" for i in
                                                    data['plugins']]) +
                                         "\n🔭插件新版本:\n" + update_check_result
                                         + "*数据来源于UnrealMultiple/TShockPlugin仓库")
        else:
            await GroupHelper.send_group(group.id, f"『插件列表』\n" +
                                         "\n".join(
                                             [f"{i['Name']} v{i['Version']} (by {i['Author']})" for i in
                                              data['plugins']]))


# 外部方法：查询服务器是否连接
def server_available(token: str):
    if token in websocket_connections:
        return True
    else:
        return False


# 外部方法：获取服务器ws对象
def get_server(token: str) -> WebSocket:
    return websocket_connections[token]


# 外部方法：通过令牌发送数据
async def send_data(token: str, data, group: int) -> None:
    data['group'] = group
    if token in websocket_connections:
        websocket = websocket_connections[token]
        logger.log(233, f"向服务器({token})发送数据: {data['type']}")
        await websocket.send_text(json.dumps(data))
    else:
        logger.error(f"数据发送失败,服务器连接不存在: {token}")


async def disconnect(token: str) -> None:
    if token in websocket_connections:
        websocket = websocket_connections[token]
        del websocket_connections[token]
        await websocket.send_text('{"type": "online","group":114514}')
    else:
        logger.error(f"断开连接失败,服务器连接不存在: {token}")


def main():
    uvicorn.run(app, host="0.0.0.0", port=22334)


start_api = get_driver()


@start_api.on_startup
def start_api_function():
    th = threading.Thread(target=main)
    th.daemon = True
    th.start()
    logger.warning("[API启动]Websocket服务器初始化完成!")
