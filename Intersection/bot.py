import nonebot

from src.adapters.MCDR import Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(Adapter)
nonebot.load_plugin("nonebot.plugins.echo")
nonebot.load_plugin("nonebot.plugins.single_session")

nonebot.run()