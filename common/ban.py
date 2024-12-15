import datetime

import nonebot


class Ban:
    def __init__(self, group: int, admin: int, reason: str, time: datetime) -> None:
        self.id = -1
        self.group = group
        self.admin = admin
        self.reason = reason
        self.time = time

    def to_dict(self):
        return {
            'group': self.group,
            'admin': self.admin,
            'reason': self.reason,
            'time': self.time.isoformat()  # 将时间转换为ISO 8601格式的字符串
        }

    @classmethod
    def from_dict(cls, data):
        data['time'] = datetime.datetime.fromisoformat(data['time'])  # 从ISO 8601格式的字符串恢复时间
        return cls(**data)

    async def to_string(self) -> str:
        try:
            name = await nonebot.get_bot().call_api("get_group_info", group_id=self.group)
            name = name['group_name']
        except:
            name = "未知群"
        return f"#⃣{name}: {self.reason} ({self.time.strftime('%Y-%m-%d')})"

    async def to_group_string(self) -> str:
        return f"#⃣{self.id}: {self.reason} ({self.time.strftime('%Y-%m-%d')})"

    async def to_details_string(self) -> str:
        try:
            name = await nonebot.get_bot().call_api("get_group_info", group_id=self.group)
            name = name['group_name']
        except:
            name = "未知群"
        return f"#⃣{name}({self.group})[{self.admin}]: {self.reason} ({self.time.strftime('%Y-%m-%d')})"
