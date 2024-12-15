import nonebot
# from nonebot.adapters.console import Adapter as ConsoleAdapter  # 避免重复命名
from nonebot.adapters.onebot.v11 import Adapter as Onebotv11
from nonebot.log import logger,default_format
from datetime import datetime
# 初始化 NoneBot

logger.add(f"logs/{datetime.today().strftime('%Y-%m-%d')}.log", level="WARNING", format=default_format, rotation="3 week")
# logging.addLevelName(233, "BotInfo")
# logger.level("BotInfo", no=45, color="<white>")
nonebot.init(log_level="WARNING")

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(Onebotv11)

nonebot.load_from_toml("pyproject.toml")
nonebot.load_plugins("plugins")
nonebot.load_plugins("plugins/commands")

if __name__ == "__main__":
    nonebot.run()
