from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot

from common.group import Group

chat = on_message()

@chat.handle()
async def chat(bot: Bot,event: GroupMessageEvent):
    if event.user_id == 1161372740:
        return
    group = Group.get_group(event.group_id)
    if group is None or not group.enable_server_bot:
        return
    if event.get_plaintext() == "":
        return
    user_info = await bot.get_group_member_info(user_id=event.user_id, group_id=event.group_id)
    user_name = user_info["card"] if user_info["card"] else user_info["nickname"]
    group_info = await bot.get_group_info(group_id=event.group_id)
    group_name = group_info['group_name']
    for i in group.chat_sync_servers:
        cmd = {
            "type": "chat",
            "group_name": group_name,
            "nickname": user_name,
            "chat_text": event.get_plaintext(),
            "group_id": event.group_id,
            "sender_id": event.user_id,
        }
        await i.send_data(cmd,group.id)



