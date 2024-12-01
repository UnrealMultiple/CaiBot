import datetime
import json
from typing import List, Optional

from utils.group_helper import GroupHelper
from utils.server import Server
from utils.sql import Sql


class Group:
    def __init__(self, id: int, admins: [int], today_bans: {datetime, int}, reject_edition: bool, auto_kick: bool,
                 kick_titled: bool, enable_server_bot: bool, servers: List[Server], config: dict) -> None:
        self.id = id
        self.admins = admins
        self.today_bans = today_bans
        self.reject_edition = reject_edition
        self.auto_kick = auto_kick
        self.kick_titled = kick_titled
        self.enable_server_bot = enable_server_bot
        self.config = config
        self.servers = servers
        try:
            self.connected_servers = [ i for i in servers if i.is_connected()]
            self.chat_sync_servers = [ i for i in servers if i.is_connected() and i.get_settings().sync_group_chat]
        except:
            self.connected_servers = []
            self.chat_sync_servers = []

    async def can_add_max(self) -> int:
        members = await GroupHelper.get_group_members(self.id)
        if members < 100:  # 群成员小于100禁止添加
            return 0
        elif 100 <= members < 300:  # 每天3个
            return 3
        elif 300 <= members < 1000:  # 每天5个
            return 5
        elif members >= 1000:  # 每天8个
            return 8

    async def can_add(self) -> bool:
        return await self.can_add_max() > self.count_bans_in_last_day()

    def add_ban(self, id: int) -> None:
        self.today_bans[datetime.datetime.now().isoformat()] = id
        self.remove_old_bans()
        self.update()

    def count_bans_in_last_day(self) -> int:
        one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
        return sum(datetime.datetime.fromisoformat(time) > one_day_ago for time in self.today_bans.keys())

    def remove_old_bans(self) -> None:
        one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
        self.today_bans = {time: id for time, id in self.today_bans.items() if
                           datetime.datetime.fromisoformat(time) > one_day_ago}

    @staticmethod
    def add_group(id: int) -> None:
        Sql.query(
            'INSERT INTO "Groups" ("id", "admins", "reject_edition", "today_bans", "auto_kick", "kick_titled",'
            '"enable_server_bot","config") '
            'VALUES (?,?,?,?,?,?,?,?);', id, json.dumps([]), 0, json.dumps({}), 0, 0, 0, json.dumps({}))

    @staticmethod
    def get_group_through_server(server: Server) -> Optional['Group']:
        return Group.get_group(server.owner)

    @staticmethod
    def get_group(id: int) -> Optional['Group']:
        result = Sql.query('SELECT * FROM "Groups" WHERE "id" = ?', id)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            servers = Server.get_group_servers(id)
            return Group(result['id'], json.loads(result['admins']), json.loads(result['today_bans']),
                         True if result['reject_edition'] == 1 else False,
                         True if result['auto_kick'] == 1 else False, True if result['kick_titled'] == 1 else False,
                         True if result['enable_server_bot'] == 1 else False, servers,
                         json.loads(result['config']))

    def update(self) -> None:
        Sql.query('UPDATE "Groups" SET "admins" = ?, "reject_edition" = ?, "today_bans" = ?, "auto_kick" = ?, '
                  '"kick_titled" = ?,"enable_server_bot" = ?,"config"=? WHERE "id" = ?;', json.dumps(self.admins),
                  self.reject_edition,
                  json.dumps(self.today_bans), 1 if self.auto_kick else 0, 1 if self.kick_titled else 0,
                  1 if self.enable_server_bot else 0, json.dumps(self.config),
                  self.id)
