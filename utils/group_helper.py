import html
import re

import nonebot
from nonebot.log import logger

from plugins.event_handle import FEEDBACK_GROUP
from utils.ban_user import UserBan
from utils.user import User

class GroupHelper:



    @staticmethod
    async def send_group(group: int, message):
        try:
            bot = nonebot.get_bot()
            await bot.call_api("send_group_msg", group_id=group, message=message)
        except Exception as ex:
            logger.warning(f"[{group}]群消息发送失败: {ex}")

    @staticmethod
    async def get_group_members_list(group_id: int):
        bot = nonebot.get_bot()
        result = await bot.call_api("get_group_member_list", group_id=group_id, no_cache=True)
        return result

    @staticmethod
    async def send_many_groups(groups: [], message: str):
        bot = nonebot.get_bot()
        for i in groups:
            await bot.call_api("send_group_msg", group_id=i, message=message)

    @staticmethod
    async def send_all_groups(message: str):
        bot = nonebot.get_bot()
        rl = await bot.call_api("get_group_list")
        rl = [i['group_id'] for i in rl]
        for i in rl:
            try:
                await bot.call_api("send_group_msg", group_id=i, message=message)
            except:
                pass

    @staticmethod
    async def kick_many_groups(groups: [], user: int):
        bot = nonebot.get_bot()
        for i in groups:
            if not GroupHelper.is_bot_admin(i):
                await GroupHelper.send_many_groups(groups, f'『云黑检测•踢出』\n' +
                                                   f"❌踢出{user}失败:\n" +
                                                   f'非本群管理员')
            await bot.call_api("set_group_kick", group_id=i, user_id=user)

    @staticmethod
    async def check_in_group(user: int):
        bot = nonebot.get_bot()
        groups = await bot.call_api("get_group_list")
        result = []
        for g in groups:
            members = await GroupHelper.get_group_members_list(g['group_id'])
            if any(member['user_id'] == user for member in members):
                result.append(g['group_id'])
        return result

    @staticmethod
    async def check_ban(user: int):
        ban = UserBan.get_user(user)
        if ban is not None and len(ban.bans) != 0:
            return len(ban.bans)
        else:
            return 0

    @staticmethod
    async def kick_check(user: int):
        ban = UserBan.get_user(user)
        if ban is not None and len(ban.bans) != 0:
            if len(ban.bans) == 1:
                groups = await GroupHelper.check_in_group(user)
                await GroupHelper.send_many_groups(groups, f'『云黑检测』\n' +
                                                   f"⚠检测新加云黑({ban.id}):\n" +
                                                   f'\n'.join([await x.to_string() for x in ban.bans]))
                return
            elif len(ban.bans) > 1:
                groups = await GroupHelper.check_in_group(user)

                await GroupHelper.send_many_groups(groups, f'『云黑检测•踢出』\n' +
                                                   f"❌踢出新加云黑({ban.id}):\n" +
                                                   f'\n'.join([await x.to_string() for x in ban.bans]))
                await GroupHelper.kick_many_groups(groups, user)


        else:
            return

    @staticmethod
    async def check_ban_many(group_id: int):
        members = await GroupHelper.get_group_members_list(group_id)
        result = []
        for i in members:
            ban = await GroupHelper.check_ban(i['user_id'])
            if ban != 0:
                result.append(f"{i['nickname']}({i['user_id']}): {ban}条云黑记录")

        return result

    @staticmethod
    async def get_group_members(group_id: int):
        bot = nonebot.get_bot()
        result = await bot.call_api("get_group_info", group_id=group_id, user_id=bot.self_id)
        return result['member_count']

    @staticmethod
    async def is_bot_admin(group_id: int):
        bot = nonebot.get_bot()
        result = await bot.call_api("get_group_member_info", group_id=group_id, user_id=bot.self_id)
        if result['role'] == 'admin' or result['role'] == 'owner':
            return True
        else:
            return False

    @staticmethod
    async def is_owner(group_id: int, qq: int):
        result = await nonebot.get_bot().call_api("get_group_member_info", group_id=group_id, user_id=qq)
        if result['role'] == 'owner':
            return True
        else:
            return False

    @staticmethod
    async def is_admin(group_id: int, qq: int):
        result = await nonebot.get_bot().call_api("get_group_member_info", group_id=group_id, user_id=qq)
        if result['role'] == 'admin' or result['role'] == 'owner':
            return True
        else:
            return False

    @staticmethod
    async def is_member(group_id: int, qq: int):
        members = await GroupHelper.get_group_members_list(group_id)
        for i in members:
            if i['user_id'] == qq:
                return True
        return False

    @staticmethod
    async def look_for_from_groups(qq: int):
        bot = nonebot.get_bot()
        rl = await bot.call_api("get_group_list")
        result = []
        for i in rl:
            try:
                if await GroupHelper.is_member(i['group_id'], qq):
                    result.append((i['group_id'], i['group_name']))
            except:
                pass
        return result

    @staticmethod
    def replace_at(data: str) -> str:  # 把cq消息中@用户 替换成纯qq
        message_text = html.unescape(data)
        at_qq = re.findall(r'\[CQ:at,qq=(\d+),name=.*\]', data)
        at_name = re.findall(r'\[CQ:at,qq=\d+,name=(.*)\]', data)
        for qq in at_qq:
            for name in at_name:
                message_text = message_text.replace(f'[CQ:at,qq={qq},name={name}]', qq)
        return message_text

    @staticmethod
    def at_to_name(data: str) -> str:
        message_text = html.unescape(data)
        at_qq = re.findall(r'\[CQ:at,qq=(\d+),name=.*\]', data)
        at_name = re.findall(r'\[CQ:at,qq=\d+,name=(.*)\]', data)
        for qq in at_qq:
            for name in at_name:
                user = User.get_user(qq)
                if user is None:
                    message_text = message_text.replace(f'[CQ:at,qq={qq},name={name}]', "[未绑定]")
                else:
                    message_text = message_text.replace(f'[CQ:at,qq={qq},name={name}]', user.name)
        return message_text

    @staticmethod
    async def HasPermission(group_id: int, qq: int):
        if qq == 3042538328:
            return True
        from utils.group import Group
        group = Group.get_group(group_id)
        if group is not None:
            if qq in group.admins:
                return True
        bot = nonebot.get_bot()
        result = await bot.call_api("get_group_member_info", group_id=group_id, user_id=qq)
        if result['role'] == 'admin' or result['role'] == 'owner':
            return True
        else:
            return False

    @staticmethod
    async def IsTitled(group_id: int, qq: int):
        result = await nonebot.get_bot().call_api("get_group_member_info", group_id=group_id, user_id=qq)
        if result['title']:
            return True
        else:
            return False

    @staticmethod
    async def GetName(qq: int):
        try:
            result = await nonebot.get_bot().call_api("get_stranger_info", user_id=qq)
            return result['nickname']
        except:
            return "无法获取昵称"

    @staticmethod
    async def GetGroupName(group: int):
        try:
            name = await nonebot.get_bot().call_api("get_group_info", group_id=group)
            name = name['group_name']
        except:
            name = "未知群"

        return name

    @staticmethod
    async def is_superadmin(user_id: int):
        return await GroupHelper.is_admin(user_id,FEEDBACK_GROUP)