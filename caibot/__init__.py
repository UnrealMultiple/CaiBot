from nonebot import get_driver, get_plugin_config
from nonebot.plugin import PluginMetadata
from .command_msg import CommandMsg
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="cai_bot",
    description="CaiBot机器人",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

from .db.database import init_db

driver = get_driver()

@driver.on_startup
async def _startup():
    await init_db()

from .command import *