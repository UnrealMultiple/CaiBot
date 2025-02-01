import asyncio
import base64
import datetime
import gzip
import io
import json
import threading
import time
import traceback
import uuid
from typing import Dict

import aiohttp
import nonebot
import requests
import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketException
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from starlette.websockets import WebSocketDisconnect

import plugins.event_handle
from common import statistics
from common.bag_png_helper import get_bag_png
from common.ban_user import UserBan
from common.group import Group
from common.group_helper import GroupHelper
from common.process_png_helper import get_process_png
from common.server import Server
from common.text_handle import TextHandle
from common.user import User, LoginRequest


class ServerConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    def add_server_connection(self, token, websocket):
        self.connections[token] = websocket

    def del_server_connection(self, token):
        if token in self.connections:
            del self.connections[token]

    def get_server_connection(self, token):
        return self.connections.get(token)

    def server_available(self, token):
        if token in self.connections:
            return True
        else:
            return False

    async def disconnect_server(self, token):
        if token in self.connections:
            try:
                await self.connections[token].close(CaiWebSocketStatus.DISCONNECT)
            except:
                pass
        else:
            logger.error(f"断开连接失败,服务器连接不存在: {token}")


    async def send_data(self, token: str, data, group: int | None) -> None:
        data['group'] = group
        if token in self.connections:
            websocket = self.connections[token]
            logger.warning(f"向服务器({token})发送数据: {data['type']}")
            await websocket.send_json(data)
        else:
            logger.error(f"数据发送失败,服务器连接不存在: {token}")


class CaiWebSocketStatus:
    NO_BIND_TOKEN = 4040
    I_IM_A_TEAPOT = 4200
    DISCONNECT = 4090


app = FastAPI()

server_connection_manager = ServerConnectionManager()
tokens = {}
online_request = {str: object}
last_connection_time = {}


def decompress_base64_gzip(base64_string):
    # 将Base64字符串解码为字节
    compressed_data = base64.b64decode(base64_string)

    # 使用GZip解压缩字节数据
    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gzip_file:
        decompressed_data = gzip_file.read()

    return decompressed_data.decode('utf-8')


def is_valid_guid(guid):
    try:
        uuid.UUID(guid, version=4)
        return True
    except ValueError:
        return False


async def wait_for_online(group_id: int, servers: list[Server]) -> [str]:
    cmd = {
        "type": "online"
    }
    result: [str] = []
    tasks = []
    for index, server in enumerate(servers):
        if server_connection_manager.server_available(server.token):
            if server.token in online_request:
                online_request.pop(server.token)
            task = asyncio.create_task(server_connection_manager.send_data(server.token, cmd, group_id))
            tasks.append(task)

    await asyncio.gather(*tasks)
    count = 0
    for index, server in enumerate(servers):
        if server_connection_manager.server_available(server.token):
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


@app.get("/bot/get_token")
async def get_token(code: int):
    current_time = datetime.datetime.now()
    if code in tokens:
        server, expiry_time = tokens[code]
        if current_time < expiry_time: # 5分钟过期
            server.add_self_server()
            tokens.pop(code)
            logger.warning(f"服务器({server.token})被动绑定成功!") # “怎么有种我是男的的感觉” ---张芷睿大人 (24.12.22)
            return {"status": 200, "token": server.token}
        else:
            tokens.pop(code)
            raise HTTPException(status_code=418, detail="token已失效!")
    else:
        raise HTTPException(status_code=418, detail="token获取失败!")


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
    logger.warning(f"收到服务器来自{server.token}({server.token})的重置通知~")
    if await GroupHelper.is_bot_admin(server.owner):
        await GroupHelper.send_group(server.owner, MessageSegment.at("all") + f"\n『自动重置』\n"
                                                                              f"[{server_name}]已重置\n"
                                                                              f"种子: {seed}")
    else:
        await GroupHelper.send_group(server.owner, f"『自动重置』\n"
                                                   f"[{server_name}]已重置\n"
                                                   f"种子: {seed}")

    for i in server.shared:
        if await GroupHelper.is_bot_admin(i):
            await GroupHelper.send_group(i, MessageSegment.at("all") + f"\n『自动重置』\n"
                                                                       f"[{server_name}]已重置\n"
                                                                       f"种子: {seed}")
        else:
            await GroupHelper.send_group(i, f"『自动重置』\n"
                                            f"[{server_name}]已重置\n"
                                            f"种子: {seed}")
    return {"status": 200}


@app.websocket("/bot/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    if not is_valid_guid(token):
        raise WebSocketException(CaiWebSocketStatus.I_IM_A_TEAPOT)
    await websocket.accept()
    server_connection_manager.add_server_connection(token, websocket)
    try:
        server = Server.get_server(token)
        if server is None:
            logger.warning(f"服务器断开连接: {token},原因：不属于任何群的服务器")
            disconnect_info = {
                "type": "delserver",
                "groupid": 114154
            }
            await websocket.send_json(disconnect_info)
            raise WebSocketException(CaiWebSocketStatus.NO_BIND_TOKEN, "不属于任何群的服务器")
        group = Group.get_group_through_server(server)
        await websocket.send_text('{"type":"hello","group":' + str(group.id) + '}')
        logger.warning(f"群服务器已连接:{group.id}({token})")
        while True:
            data = await websocket.receive_text()
            if not server_connection_manager.server_available(token):
                raise WebSocketDisconnect(CaiWebSocketStatus.DISCONNECT,"无效连接")
            try:
                await handle_message(data, group, token, server, websocket)
            except Exception:
                logger.error(f"群服务器{group.id}({token}):{traceback.format_exc()}")
    except WebSocketDisconnect as e:
        logger.warning(f"服务器断开连接: {token},原因：{str(e)}")
    except Exception as e:
        logger.warning(f"服务器断开连接: {token},原因：{str(e)}")
        await websocket.close()
    finally:
        server_connection_manager.del_server_connection(token)


login_attempts = {}
login_requests = {}
last_sent_warning_times = {}


async def handle_message(data: str, group: Group, token: str, server: Server, websocket) -> None:
    data = json.loads(data)
    if 'group' in data:
        if data['group'] != server.owner and data['group'] not in server.shared:
            return
        group = group.get_group(data['group'])
    index = server.get_server_index(group.id)
    if data['type'] != 'HeartBeat':
        logger.warning(f"收到来自{group.id}({token})的数据: {data['type']}")
    if data['type'] == "hello":
        # "tshock_version":"5.2.0.0","plugin_version":"2024.6.7.0","terraria_version":"v1.4.4.9","cai_whitelist":false,"os":"win10-x64"
        websocket.tshock_version = data['tshock_version']
        websocket.plugin_version = data['plugin_version']
        websocket.terraria_version = data['terraria_version']
        websocket.whitelist = data['cai_whitelist']
        websocket.world = data['world']
        websocket.os = data['os']
        try:
            websocket.sync_group_chat = data['sync_group_chat']
            websocket.sync_server_chat = data['sync_server_chat']
        except:
            websocket.sync_group_chat = False
            websocket.sync_server_chat = False

        plugins.cai_api.server_connection_manager.connections[token] = websocket
        group_info = {
            "type": "groupid",
            "groupid": int(group.id)
        }
        logger.warning(f"获取到{group.id}({token})的服务器信息: \n"
                       f"CaiBot版本: {data['plugin_version']}, TShock版本: {data['tshock_version']}, Cai白名单: {data['cai_whitelist']}, 系统:{data['os']}")
        await websocket.send_text(json.dumps(group_info))
    elif data['type'] == "cmd":
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
        try:
            progress_img = get_process_png(data)
        except:
            await GroupHelper.send_group(group.id,f"『需要更新』\n"
                                                   f"请使用最新版的CaiBot适配插件!")
            return
        byte_arr = io.BytesIO()
        progress_img.save(byte_arr, format='PNG')
        byte_value = byte_arr.getvalue()
        await GroupHelper.send_group(group.id, message=MessageSegment.image(byte_value))
    elif data['type'] == "process_text":
        await GroupHelper.send_group(group.id, f"『进度查询』\n" + data['process'])
    elif data['type'] == "whitelist":

        re = {
            "type": "whitelist",
            "name": data['name'],
            "code": 501,
            "uuids": []
        }
        await server_connection_manager.send_data(token, re, None)

        group_id = group.id
        now = datetime.datetime.now()
        if group_id not in last_sent_warning_times or now - last_sent_warning_times[group_id] > datetime.timedelta(
                hours=1):
            last_sent_warning_times[group_id] = now
            await GroupHelper.send_group(group_id, f"『需要更新』\n"
                                                   f"CaiBot无法完成白名单校验!\n"
                                                   f"请更新服务器[{index}]的插件/MOD到最新版本~")
        return
    elif data['type'] == "whitelistV2":
        if websocket.plugin_version == "2024.10.13.1":
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 404
            }
            await server_connection_manager.send_data(token, re, None)
            group_id = group.id
            now = datetime.datetime.now()
            if group_id not in last_sent_warning_times or now - last_sent_warning_times[group_id] > datetime.timedelta(
                    hours=1):
                last_sent_warning_times[group_id] = now
                await GroupHelper.send_group(group_id, f"『需要更新』\n"
                                                       f"无法校验白名单!\n"
                                                       f"请更新服务器[{index}]的插件/MOD到最新版本~")
            return
        if websocket.plugin_version == "2024.10.12.1":
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 404
            }
            await server_connection_manager.send_data(token, re, None)
            group_id = group.id
            now = datetime.datetime.now()
            if group_id not in last_sent_warning_times or now - last_sent_warning_times[group_id] > datetime.timedelta(
                    hours=1):
                last_sent_warning_times[group_id] = now
                await GroupHelper.send_group(group_id, f"『需要更新』\n"
                                                       f"不安全的插件版本!\n"
                                                       f"请更新服务器[{index}]的插件/MOD到最新版本~")
            return

        name = data['name']
        plr_uuid = data['uuid']
        current_time = time.time()
        ip = data['ip']
        user = User.get_user_name(name)
        statistics.Statistics.add_check_whitelist()
        if plr_uuid is None or not is_valid_guid(plr_uuid):
            return
        if user is None:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 404
            }
            await server_connection_manager.send_data(token, re, None)
            return
        ban = UserBan.get_user(user.id)
        if ban is not None and len(ban.bans) > 1:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 403
            }
            await server_connection_manager.send_data(token, re, None)
            return
        if ban is not None and ban.check_ban(user.id):
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 403
            }
            await server_connection_manager.send_data(token, re, None)
            return
        member = False
        try:
            if await GroupHelper.is_member(group.id, user.id):
                member = True
            else:
                for i in server.shared:
                    if await GroupHelper.is_member(i, user.id):
                        member = True
                        break
        except:
            member = True
        if not member:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 401
            }

            await server_connection_manager.send_data(token, re, None)
            return
        safe_uuid = plr_uuid if ip == "127.0.0.1" else plr_uuid + "+" + ip
        if safe_uuid in user.uuid:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 200
            }
            await server_connection_manager.send_data(token, re, None)
        else:
            re = {
                "type": "whitelist",
                "name": data['name'],
                "code": 405
            }

            if (ip not in login_attempts or current_time - login_attempts[ip] >= 60 * 2) or ip == "127.0.0.1":
                login_attempts[ip] = current_time

                same_device_users = User.get_users_uuid(plr_uuid)
                same_device_users = [i for i in same_device_users if i.id != user.id]
                login_requests[user.id] = LoginRequest(datetime.datetime.now(),
                                                       plr_uuid if ip == "127.0.0.1" else plr_uuid + "+" + ip)
                await server_connection_manager.send_data(token, re, None)
                if len(same_device_users) == 0:
                    if await GroupHelper.is_member(server.owner, user.id):
                        await GroupHelper.send_group(server.owner, message=MessageSegment.at(user.id) +
                                                                           f"\n『登录请求』\n" +
                                                                           f"有新的设备请求登录您的账号\n" +
                                                                           f"✅回复'登录'允许登录\n" +
                                                                           f"❌回复'拒绝'拒绝登录")
                        return
                    for i in server.shared:
                        if await GroupHelper.is_member(i, user.id):
                            await GroupHelper.send_group(i, message=MessageSegment.at(user.id) +
                                                                    f"\n『登录请求』\n" +
                                                                    f"有新的设备请求登录您的账号\n" +
                                                                    f"✅回复'登录'批准登录\n" +
                                                                    f"❌回复'拒绝'拒绝登录")
                            return
                else:
                    if await GroupHelper.is_member(server.owner, user.id):
                        await GroupHelper.send_group(server.owner, message=MessageSegment.at(user.id) +
                                                                           f"\n『登录请求』\n" +
                                                                           f"有新的设备请求登录您的账号\n" +
                                                                           "⚠️此设备登录过以下账户:\n" +
                                                                           ",".join([f"{i.name}({i.id})" for i in
                                                                                     same_device_users]) +
                                                                           f"\n✅回复'登录'批准登录\n" +
                                                                           f"❌回复'拒绝'拒绝登录")
                        return
                    for i in server.shared:
                        if await GroupHelper.is_member(i, user.id):
                            await GroupHelper.send_group(i, message=MessageSegment.at(user.id) +
                                                                    f"\n『登录请求』\n" +
                                                                    f"有新的设备请求登录您的账号\n" +
                                                                    "⚠️此设备登录过以下账户:\n" +
                                                                    ",".join([f"{i.name}({i.id})" for i in
                                                                              same_device_users]) +
                                                                    f"\n✅回复'登录'批准登录\n" +
                                                                    f"❌回复'拒绝'拒绝登录")
                            return
            else:
                await server_connection_manager.send_data(token, re, None)
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
            if 'life' not in data:
                data['life'] = "插件过旧"
                data['mana'] = "插件过旧"
                data['quests_completed'] = -1
                data['enhances'] = []
                await GroupHelper.send_group(group.id, f"『查背包』\n" +
                                             f"✨新版插件新增基本信息和Economic查询\n"
                                             f"请及时升级插件哦~")

            if 'life' in data and 'economic' not in data:
                data['economic'] = {"Coins": "", "LevelName": "", "Skill": ""}
                await GroupHelper.send_group(group.id, f"『查背包』\n" +
                                             f"✨新版插件新增Economic查询\n"
                                             f"请及时升级插件哦~")
            data['economic']['Coins'] = TextHandle.all(data['economic']['Coins'])
            data['economic']['LevelName'] = TextHandle.all(data['economic']['LevelName'])
            data['economic']['Skill'] = TextHandle.add_line_break(TextHandle.all(data['economic']['Skill']), 9)
            img = get_bag_png(data['name'], data['inventory'], data['buffs'], data['enhances'], data['life'],
                              data['mana'], data['quests_completed'], data['economic'])
            byte_arr = io.BytesIO()
            img.save(byte_arr, format='PNG')
            byte_value = byte_arr.getvalue()
            await GroupHelper.send_group(group.id, message=MessageSegment.image(byte_value))
    elif data['type'] == "lookbag_text":
        await GroupHelper.send_group(group.id, f"『查背包』\n" + data['inventory'])
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
        tshock_plugins = data['plugins']
        tshock_plugins.sort(key=lambda x: x['Name'])
        has_new_version = False
        remote_plugins = requests.get("http://api.terraria.ink:11434/plugin/get_plugin_list").json()
        for local in tshock_plugins:
            for remote in remote_plugins:
                if local["Name"] == remote["Name"]:
                    if list(map(int, local['Version'].split('.'))) < list(map(int, remote['Version'].split('.'))):
                        has_new_version = True
                        update_check_result += f"[{local['Name']}] v{local['Version']} >>> v{remote['Version']}\n"

        if has_new_version:
            await GroupHelper.send_group(group.id, f"『插件列表』\n" +
                                         "\n".join([f"{i['Name']} v{i['Version']}" for i in
                                                    tshock_plugins]) +
                                         "\n🔭插件新版本:\n" + update_check_result
                                         + "*数据来源于UnrealMultiple/TShockPlugin仓库")
        else:
            await GroupHelper.send_group(group.id, f"『插件列表』\n" +
                                         "\n".join(
                                             [f"{i['Name']} v{i['Version']}" for i in
                                              tshock_plugins]))
    elif data['type'] == "modlist":
        mods = data['mods']
        mods.sort(key=lambda x: x['Name'])
        await GroupHelper.send_group(group.id, f"『TMOD列表』\n" +
                                     "\n".join(
                                         [f"{i['Name']} v{i['Version']}" for i in
                                          mods]))
    elif data['type'] == "post_ban_add":
        await GroupHelper.send_group(server.owner, f"『Ban封禁』\n"
                                                   f"玩家名: {data['name']}\n"
                                                   f"理由: {data['reason']}\n"
                                                   f"执行者: {data['admin']}\n"
                                                   f"到期时间: {data['expire_time']}")

        for i in server.shared:
            await GroupHelper.send_group(i, f"『Ban封禁』\n"
                                            f"玩家名: {data['name']}\n"
                                            f"理由: {data['reason']}\n"
                                            f"执行者: {data['admin']}\n"
                                            f"到期时间: {data['expire_time']}")
    elif data['type'] == "chat":
        return
        url = "http://127.0.0.1:8082/send_group_chat"
        data['chat'] = TextHandle.all(data['chat'])
        session = aiohttp.ClientSession()
        data = {'chat': data['chat'], 'groupid': server.owner}
        await session.post(url, json=data)
        await session.close()
        for i in server.shared:
            session = aiohttp.ClientSession()
            data = {'chat': data['chat'], 'groupid': i}
            await session.post(url, json=data)
            await session.close()


start_api = get_driver()


@start_api.on_startup
def start_api_function():
    def api_main():
        uvicorn.run(app, host="0.0.0.0", port=22334)
    th = threading.Thread(target=api_main)
    th.daemon = True
    th.start()
    logger.warning("[API启动]Websocket服务器初始化完成!")
