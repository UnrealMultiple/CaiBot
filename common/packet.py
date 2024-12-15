# class BasePacket:
#     def __init__(self, data):
#         self.type = data['type']
#
#     def process(self, group, token, websocket):
#         raise NotImplementedError("This method should be overridden in subclasses")
#
# class HelloPacket(BasePacket):
#     def __init__(self, data):
#         super().__init__(data)
#         self.tshock_version = data['tshock_version']
#         self.plugin_version = data['plugin_version']
#         self.terraria_version = data['terraria_version']
#         self.cai_whitelist = data['cai_whitelist']
#         self.os = data['os']
#         self.sync_group_chat = data.get('sync_group_chat', False)
#         self.sync_server_chat = data.get('sync_server_chat', False)
#
#     def process(self, group, token, websocket):
#         # 处理 hello 数据包
#         websocket.tshock_version = self.tshock_version
#         websocket.plugin_version = self.plugin_version
#         websocket.terraria_version = self.terraria_version
#         websocket.whitelist = self.cai_whitelist
#         websocket.os = self.os
#         websocket.sync_group_chat = self.sync_group_chat
#         websocket.sync_server_chat = self.sync_server_chat
#
#         plugins.API.websocket_connections[token] = websocket
#         group_info = {
#             "type": "groupid",
#             "groupid": int(group.id)
#         }
#         logger.warning(f"获取到{group.id}({token})的服务器信息: \n"
#                        f"CaiBot版本: {self.plugin_version}, TShock版本: {self.tshock_version}, Cai白名单: {self.cai_whitelist}, 系统:{self.os}")
#         await websocket.send_text(json.dumps(group_info))
#
# class CmdPacket(BasePacket):
#     def __init__(self, data):
#         super().__init__(data)
#         self.result = data['result']
#         self.at = data['at']
#
#     def process(self, group, token, websocket):
#         # 处理 cmd 数据包
#         if self.result:
#             await GroupHelper.send_group(group.id, MessageSegment.at(self.at) + f"\n『远程指令』\n"
#                                            f"服务器[{index}]返回如下结果:\n" + TextHandle.all(self.result))
#         else:
#             await GroupHelper.send_group(group.id, f"『远程指令』\n服务器[{index}]返回了个寂寞")
#
