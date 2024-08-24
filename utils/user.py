import datetime
import json

from utils.sql import Sql


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
                 uuid: list, login_request,last_rename) -> None:
        self.id = id
        self.name = name
        self.join_group = join_group
        self.money = money
        self.last_sign = last_sign
        self.sign_count = sign_count
        self.uuid = uuid
        self.login_request = login_request
        self.last_rename = last_rename

    @staticmethod
    def get_sign_rank():
        return Sql.query("SELECT COUNT(*) as num FROM Users WHERE DATE(last_sign) = DATE('now','localtime');")[0]['num']

    @staticmethod
    def add_user(id: int, name: str, group: int):
        Sql.query(
            'INSERT INTO "Users" ("id", "name", "join_group", "money", "last_sign","sign_count","uuid",'
            '"login_request","last_rename") '
            'VALUES (?,?,?,?,?,?,?,?,?);', id, name, json.dumps([group]), 0, datetime.datetime.min.isoformat(), 0, "[]",
            json.dumps(LoginRequest(datetime.datetime.min, "").to_dict()),datetime.datetime.min.isoformat())
        return User(id, name, [group], 0, datetime.datetime.min, 0, [], LoginRequest(datetime.datetime.min, ""),datetime.datetime.min)

    @staticmethod
    def get_user(id: int):
        result = Sql.query('SELECT * FROM "Users" WHERE "id" = ?', id)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return User(result['id'], result['name'], json.loads(result['join_group']), result['money'],
                        datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                        json.loads(result['uuid']), LoginRequest.from_dict(json.loads(result['login_request'])),datetime.datetime.fromisoformat(result['last_rename']))

    @staticmethod
    def get_user_name(name: str):
        result = Sql.query('SELECT * FROM "Users" WHERE "name" = ?', name)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return User(result['id'], result['name'], json.loads(result['join_group']), result['money'],
                        datetime.datetime.fromisoformat(result['last_sign']), result['sign_count'],
                        json.loads(result['uuid']), LoginRequest.from_dict(json.loads(result['login_request'])),datetime.datetime.fromisoformat(result['last_rename']))

    @staticmethod
    def get_users_group(group: int):
        result = Sql.query('SELECT * FROM "Users" WHERE "join_group" like ?', group)
        re = []
        for i in result:
            re.append(User(i['id'], i['name'], json.loads(i['join_group']), i['money'],
                           datetime.datetime.fromisoformat(i['last_sign']), i['sign_count'],
                           json.loads(i['uuid']), LoginRequest.from_dict(json.loads(result['login_request'])),datetime.datetime.fromisoformat(result['last_rename'])))

    def update(self):
        Sql.query('UPDATE "Users" SET "name" = ?, "join_group" = ?, "money" = ?, '
                  '"last_sign" = ? ,"sign_count" = ?,"uuid" = ? , "login_request" = ? ,"last_rename" = ?  WHERE "id" '
                  '= ?;', self.name,
                  json.dumps(self.join_group), self.money, self.last_sign.isoformat(), self.sign_count,json.dumps(self.uuid),
                  json.dumps(self.login_request.to_dict()),self.last_rename.isoformat() ,self.id)
