from typing import Optional

from common.sql import Sql


class Statistics:
    def __init__(self, total_group: int, total_ban, total_kick: int, total_check: int, check_whitelist: int,
                 total_users: int, total_servers: int) -> None:
        self.total_group = total_group
        self.total_ban = total_ban
        self.total_kick = total_kick
        self.total_check = total_check
        self.check_whitelist = check_whitelist
        self.total_users = total_users
        self.total_servers = total_servers

    @staticmethod
    def get_statistics() -> Optional['Statistics']:
        re = Sql.query('SELECT * FROM "Statistics" WHERE rowid = 1;')
        total_kick = re[0]['total_kick']
        total_check = re[0]['total_check']
        check_whitelist = re[0]['check_whitelist']
        re = Sql.query('SELECT COUNT(*) AS nums FROM "Groups";')
        total_group = re[0]['nums']
        re = Sql.query('SELECT COUNT(*) AS nums FROM "Bans" WHERE bans != \'[]\';')
        total_ban = re[0]['nums']
        re = Sql.query('SELECT COUNT(*) AS nums FROM "Users"')
        total_users = re[0]['nums']
        re = Sql.query('SELECT COUNT(*) AS nums FROM "Servers"')
        total_servers = re[0]['nums']
        return Statistics(total_group, total_ban, total_kick, total_check, check_whitelist, total_users, total_servers)

    @staticmethod
    def add_kick() -> None:
        statistics = Statistics.get_statistics()
        Sql.query('UPDATE "Statistics" SET "total_kick" = ? WHERE rowid = 1;', statistics.total_kick + 1)

    @staticmethod
    def add_check() -> None:
        statistics = Statistics.get_statistics()
        Sql.query('UPDATE "Statistics" SET "total_check" = ? WHERE rowid = 1;', statistics.total_check + 1)

    @staticmethod
    def add_check_whitelist() -> None:
        statistics = Statistics.get_statistics()
        Sql.query('UPDATE "Statistics" SET "check_whitelist" = ? WHERE rowid = 1;', statistics.check_whitelist + 1)
