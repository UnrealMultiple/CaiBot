import json
from typing import List

import utils.server
from utils.sql import Sql


class Server:

    def __init__(self, token: str, owner: int, shared: List[int], ip: str, port: int) -> None:
        self.owner = owner
        self.token = token
        self.shared = shared
        self.ip = ip
        self.port = port

    @staticmethod
    def add_server(token: str, owner: int, ip: str, port: int) -> None:
        Sql.query(
            'INSERT INTO "Servers" ("token", "owner", "shared", "ip", "port") '
            'VALUES (?,?,?,?,?);', token, owner, json.dumps([]), ip, port)

    def add_self_server(self) -> None:
        Sql.query(
            'INSERT INTO "Servers" ("token", "owner", "shared", "ip", "port") '
            'VALUES (?,?,?,?,?);', self.token,self.owner, json.dumps([]), self.ip,self.port)

    @staticmethod
    def del_server(token: str) -> None:
        Sql.query(
            'DELETE FROM "Servers" WHERE "token" = ?', token)

    @staticmethod
    def get_server(token: str):
        result = Sql.query('SELECT * FROM "Servers" WHERE "token" = ?', token)
        if len(result) == 0:
            return None
        else:
            result = result[0]
            return Server(result['token'], result['owner'], json.loads(result['shared']), result['ip'], result['port'])

    @staticmethod
    def get_group_servers(id: int) -> List:
        results = Sql.query('SELECT * FROM "Servers" WHERE "owner" = ?', id)
        results.extend(Sql.query("SELECT * FROM Servers WHERE shared LIKE ?", '%' + str(id) + '%'))
        if len(results) == 0:
            return []
        else:
            return [Server(result['token'], result['owner'], json.loads(result['shared']), result['ip'], result['port'])
                    for result in results if result['owner'] == id or id in json.loads(result['shared'])]

    def get_server_index(self, id: int) -> int:
        servers = Server.get_group_servers(id)
        index = 1
        for i in servers:
            if i.token == self.token:
                return index
            index += 1

    def is_owner_server(self, id: int) -> bool:
        return self.owner == id

    def update(self) -> None:
        Sql.query('UPDATE "Servers" SET "owner" = ?, "shared" = ?, "ip" = ?,"port" = ? WHERE "token" = ?;',
                  self.owner, json.dumps(self.shared), self.ip, self.port, self.token)
