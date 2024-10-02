import nonebot
# from nonebot.adapters.console import Adapter as ConsoleAdapter  # 避免重复命名
from nonebot.adapters.onebot.v11 import Adapter as Onebotv11

# 初始化 NoneBot
nonebot.init(log_level="WARNING")
# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(Onebotv11)

nonebot.load_from_toml("pyproject.toml")
nonebot.load_plugins("plugins")
nonebot.load_plugins("plugins/commands")

if __name__ == "__main__":
    nonebot.run()
