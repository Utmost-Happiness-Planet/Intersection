import nonebot
from nonebot.adapters.onebot.v11 import Adapter as onebot

from src.adapters.MCDR import Adapter as MCDR

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(MCDR)
driver.register_adapter(onebot)
nonebot.load_plugin("nonebot.plugins.echo")
nonebot.load_plugin("nonebot.plugins.single_session")

nonebot.run()