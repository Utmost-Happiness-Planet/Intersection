import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from src.adapters.MCDR import Adapter as MCDRAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
driver.register_adapter(MCDRAdapter)

nonebot.load_builtin_plugins('echo', 'single_session')


# nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()
