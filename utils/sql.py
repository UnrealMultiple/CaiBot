import sqlite3
from typing import List

from nonebot import get_driver
from nonebot.log import logger


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Sql:
    sql = None

    def __init__(self) -> None:
        conn = sqlite3.connect("bot.db", check_same_thread=False)
        conn.row_factory = dict_factory

        self.conn = conn
        Sql.sql = self

    @staticmethod
    def query(cmd: str, *args) -> List['dict']:
        cursor = Sql.sql.conn.cursor()
        cursor.execute(cmd, args)
        Sql.sql.conn.commit()
        return cursor.fetchall()


start_sql = get_driver()


@start_sql.on_startup
def start_api_function():
    Sql()
    logger.warning("[Sqlite启动]数据库初始化完成!")
