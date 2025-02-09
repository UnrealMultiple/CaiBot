import datetime
import json
from typing import Optional

from common.sql import Sql


class LoginRequest:
    def __init__(self, time: datetime.datetime, uuid: str) -> None:
        self.uuid = uuid
        self.time = time

    def to_dict(self):
        return {
            'time': self.time.isoformat(),
            'uuid': self.uuid
        }

    @classmethod
    def from_dict(cls, data):
        data['time'] = datetime.datetime.fromisoformat(data['time'])  # 从ISO 8601格式的字符串恢复时间
        return cls(**data)


class User:
    def __init__(self, id: int, name: str, join_group: list, money: int, last_sign: datetime.datetime, sign_count: int,
                 uuid: list, last_rename) -> None:
        self.id = id
        self.name = name
        self.join_group = join_group
        self.money = money
        self.last_sign = last_sign
        self.sign_count = sign_count
        self.uuid = uuid
        self.last_rename = last_rename

    @staticmethod
    def get_sign_rank() -> int:
        return Sql.query("SELECT COUNT(*) as num FROM Users WHERE DATE(last_sign) = DATE('now','localtime');")[0]['num']

    @staticmethod
    def add_user(id: int, name: str, group: int) -> Optional['User'] | None:
        Sql.query(
            'INSERT INTO "Users" ("id", "name", "join_group", "money", "last_sign","sign_count","uuid",'
            '"last_rename") '
            'VALUES (?,?,?,?,?,?,?,?);', id, name, json.dumps([group]), 0, datetime.datetime.min.isoformat(), 0, "[]", datetime.datetime.min.isoformat())
        return User(id, name, [group], 0, datetime.datetime.min, 0, [],
                    datetime.datetime.min)

    @staticmethod
    def get_user(id: int) -> Optional['User'] | None:
        result = Sql.query('SELECT * FROM "Users" WHERE "id" = ?', id)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return User(result['id'], result['name'], json.loads(result['join_group']), result['money'],
                        datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                        json.loads(result['uuid']),
                        datetime.datetime.fromisoformat(result['last_rename']))

    @staticmethod
    def get_user_name(name: str) -> Optional['User'] | None:
        result = Sql.query('SELECT * FROM "Users" WHERE "name" = ?', name)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return User(result['id'], result['name'], json.loads(result['join_group']), result['money'],
                        datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                        json.loads(result['uuid']),datetime.datetime.fromisoformat(result['last_rename']))

    @staticmethod
    def get_users_uuid(uuid: str) -> list['User']:
        query = 'SELECT * FROM "Users" WHERE "uuid" LIKE ?'
        results = Sql.query(query, '%' + uuid + '%')
        re = []
        for result in results:
            re.append(User(result['id'], result['name'], json.loads(result['join_group']), result['money'],
                        datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                        json.loads(result['uuid']),
                        datetime.datetime.fromisoformat(result['last_rename'])))
        return re


    @staticmethod
    def get_users_group(group: int) -> list['User']:
        query = 'SELECT * FROM "Users" WHERE "join_group" LIKE ?'
        results = Sql.query(query, '%' + str(group) + '%')
        re = []
        for result in results:
            re.append(User(result['id'], result['name'], json.loads(result['join_group']), result['money'],
                           datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                           json.loads(result['uuid']),
                           datetime.datetime.fromisoformat(result['last_rename'])))
        return re

    def update(self) ->None :
        Sql.query('UPDATE "Users" SET "name" = ?, "join_group" = ?, "money" = ?, '
                  '"last_sign" = ? ,"sign_count" = ?,"uuid" = ? ,"last_rename" = ?  WHERE "id" '
                  '= ?;', self.name,
                  json.dumps(self.join_group), self.money, self.last_sign.isoformat(), self.sign_count,
                  json.dumps(self.uuid), self.last_rename.isoformat(), self.id)
