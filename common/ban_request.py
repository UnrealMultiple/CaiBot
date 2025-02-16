import datetime
from typing import Optional

import nonebot

from common.sql import Sql


class BanRequest:
    def __init__(self, id: int, target: int, group: int, admin: int, reason: str, time: datetime, handled: bool):
        self.id = id
        self.target = target
        self.group = group
        self.admin = admin
        self.reason = reason
        self.time = time
        self.handled = handled

    async def to_oneline_string(self) -> str:
        try:
            name = await nonebot.get_bot().call_api("get_group_info", group_id=self.group)
            name = name['group_name']
        except:
            name = "未知群"
        return f"[{self.id}] {self.target} by {name}({self.group})  理由: {self.reason}"

    @staticmethod
    def add(target: int, group: int, admin: int, reason: str) -> int:
        id = Sql.query('SELECT COUNT(*) AS nums FROM "BanRequests"')[0]['nums'] + 1
        Sql.query(
            'INSERT INTO "BanRequests" ("id", "target", "group", "admin", "reason", "time", "handled") '
            'VALUES (?, ?, ?, ?, ?, ?, ?);',
            id, target, group, admin, reason, datetime.datetime.now().isoformat(), 0
        )
        return id

    def update(self) -> None:
        Sql.query(
            'UPDATE "BanRequests" SET "target" = ?, "group" = ?, "admin" = ?, "reason" = ?, "time" = ?, "handled" = ? '
            'WHERE "id" = ?;',
            self.target, self.group, self.admin, self.reason, self.time.isoformat(), 1 if self.handled else 0 , self.id
        )

    @staticmethod
    def get_by_id(id: int) -> Optional['BanRequest']:
        result = Sql.query('SELECT * FROM "BanRequests" WHERE "id" = ?', id)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return BanRequest(
                id=result['id'],
                target=result['target'],
                group=result['group'],
                admin=result['admin'],
                reason=result['reason'],
                time=datetime.datetime.fromisoformat( result['time']),
                handled= True if result['handled']==1 else False
            )

    @staticmethod
    def get_by_target_and_group(target: int, group: int) -> Optional['BanRequest']:
        result = Sql.query('SELECT * FROM "BanRequests" WHERE "target" = ? AND "group" = ? AND "handled" = 0', target, group)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return BanRequest(
                id=result['id'],
                target=result['target'],
                group=result['group'],
                admin=result['admin'],
                reason=result['reason'],
                time=datetime.datetime.fromisoformat( result['time']),
                handled= True if result['handled']==1 else False
            )

    @staticmethod
    def get_by_group(group: int) -> list['BanRequest']:
        results = Sql.query('SELECT * FROM "BanRequests" WHERE "group" = ?',  group)
        re = []
        for result in results:
            re.append(BanRequest(
                id=result['id'],
                target=result['target'],
                group=result['group'],
                admin=result['admin'],
                reason=result['reason'],
                time=datetime.datetime.fromisoformat( result['time']),
                handled=True if result['handled'] == 1 else False))

        return re

    @staticmethod
    def get_all() -> list['BanRequest']:
        results = Sql.query('SELECT * FROM "BanRequests" WHERE "handled" ==0 ')
        re = []
        for result in results:
            re.append(BanRequest(
                id=result['id'],
                target=result['target'],
                group=result['group'],
                admin=result['admin'],
                reason=result['reason'],
                time=datetime.datetime.fromisoformat( result['time']),
                handled=True if result['handled'] == 1 else False))

        return re
