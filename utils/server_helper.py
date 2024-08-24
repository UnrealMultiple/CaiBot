import asyncio
import math
import re
import socket
import time
from nonebot.log import logger


def createMessage(type, message, debug=False):
    ret = [len(message) + 3, 0, type]
    for i in range(len(message)):
        if message[i] == "byte":
            message[i] = 0
        if message[i] > 255:
            if message[i + 1] != "byte":
                message[i] %= 256
            else:
                message[i + 1] = int(message[i] / 256)
                message[i] %= 256
        ret.append(message[i])
    return ret


def is_Chinese(ch):
    return '\u4e00' <= ch <= '\u9fff'


def aToD(string):
    return [ord(c) for c in string]


def cToD(string: str):
    string = string.encode("utf-8")
    string = str(string).replace("b'", "").replace("'", "").split(r"\x")
    string.remove('')
    return [int(i, 16) for i in string]


def strForm(arr):
    return [len(arr)] + arr


async def send(s, message):
    s.sendall(bytes(message))


def send_password(password):
    key = [4 + len(password), 0, 38, len(password)] + aToD(password)
    return key


async def request(s):
    received = await asyncio.to_thread(s.recv, 65536)
    msgtype, data = int(received[2]), received[3:]

    if msgtype == 2:
        data = data.decode(errors="ignore")
        result = ''.join(c for c in data if c.isalnum() or c == '-')
        logger.log(233, f"收到添加服务器数据: {result}")
        return result
    return None


async def ping_request(s):
    received = await asyncio.to_thread(s.recv, 65536)
    msgtype, data = int(received[2]), received[3:]
    data = data.decode(errors="ignore")
    return msgtype, data


def buildMsgDataPack(str):
    strlen = sum(3 if is_Chinese(i) else 1 for i in str)
    res = [10 + strlen, 0, 82, 1, 0, 3, 83, 97, 121, strlen]
    for i in str:
        if is_Chinese(i):
            res += cToD(i)
        else:
            res += aToD(i)
    return res


async def joinServer(s, code):
    version_msg = createMessage(217, strForm(aToD(str(code))))
    await send(s, version_msg)
    data = await request(s)
    return data


async def sendMsg(s, msg):
    await send(s, buildMsgDataPack(msg))


async def set_server(adr: str, port: int, code: int):
    loop = asyncio.get_event_loop()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        await loop.run_in_executor(None, s.connect, (socket.gethostbyname(adr), port))
        return await joinServer(s, code)


async def ping_server(adr: str, port: int):
    loop = asyncio.get_event_loop()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        await loop.run_in_executor(None, s.connect, (adr, port))
        start_time = time.time()
        version_msg = createMessage(1, strForm(aToD(str("CaiBot"))))
        await send(s, version_msg)
        pack, data = await ping_request(s)
        end_time = time.time()
        return (end_time - start_time) * 1000, pack
