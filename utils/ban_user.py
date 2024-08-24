import datetime
import json
import random
import smtplib
import sqlite3
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import sql_setting
import pymysql
import requests
import requests as rq
import datetime

from utils.ban import Ban
from utils.sql import Sql


class UserBan:
    def __init__(self, id: int, bans: list, has_kicked: int, trust_ban: bool, trust_ban_reason: str) -> None:
        self.id = id
        self.bans = bans
        self.has_kicked = has_kicked
        self.trust_ban = trust_ban
        self.trust_ban_reason = trust_ban_reason

    def add_ban(self, group: int, admin: int, reason: str):
        self.bans.append(Ban(group, admin, reason, datetime.datetime.now()))
        self.update_user()

    def del_ban(self, group: int):
        self.bans = [n for n in self.bans if n.group != group]
        self.update_user()

    def get_ban(self, group: int):
        for i in self.bans:
            if i.owner == group:
                return i
        return None



    def check_ban(self, group: int):
        if any(n.group == group for n in self.bans):
            return True
        else:
            return False

    def check_ban_user(self, admin: int):
        if any(n.admin == admin for n in self.bans):
            return True
        else:
            return False

    @staticmethod
    def add_user(id: int):
        Sql.query('INSERT INTO "Bans" ("id", "bans", "has_kicked", "trust_ban", "trust_ban_reason") '
                  'VALUES (?,?,?,?,?);', id, json.dumps([]), 0, 0, "")
        return UserBan(id, [], False, False, "")

    @staticmethod
    def get_user(id: int):
        result = Sql.query('SELECT * FROM "Bans" WHERE "id" = ?', id)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return UserBan(result['id'], [Ban.from_dict(data) for data in json.loads(result['bans'])],
                           result['has_kicked'],
                           True if result['trust_ban'] else False, result['trust_ban_reason'])

    @staticmethod
    def get_all_bans():
        result = Sql.query('SELECT * FROM "Bans" WHERE bans != \'[]\'')
        user_list = [UserBan(result['id'], [Ban.from_dict(data) for data in json.loads(result['bans'])],
                           result['has_kicked'],
                           True if result['trust_ban'] else False, result['trust_ban_reason']) for result in result]
        return user_list

    @staticmethod
    def get_users():
        result = Sql.query('SELECT * FROM "Bans"')
        re = []
        if len(result) == 0:
            return re
        else:
            for i in result:
                re.append(UserBan(result['id'], [Ban.from_dict(data) for data in json.loads(result['bans'])],
                                  result['has_kicked'],
                                  True if result['trust_ban'] else False, result['trust_ban_reason']))
            return re

    def update_user(self):
        Sql.query('UPDATE "Bans" SET "bans" = ?, "has_kicked" = ?, "trust_ban" = ?, '
                  '"trust_ban_reason" = ? WHERE "id" = ?;', json.dumps([ban.to_dict() for ban in self.bans]),
                  self.has_kicked, self.trust_ban, self.trust_ban_reason, self.id)
