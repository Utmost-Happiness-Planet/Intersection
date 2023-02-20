from nonebot import get_driver, logger

config = get_driver().config.dict()
if 'schematic_command' not in config:
    logger.warning('[原理图系统] 未发现配置项 `schematic_command` , 采用默认值: "schematic"')
if 'schematic_folder' not in config:
    logger.error('[原理图系统] 未发现配置项 `schematic_folder` , 请指定原理图目录')
    raise Exception('[原理图系统] 未发现配置项 `schematic_folder` , 请指定原理图目录')

schematic_command = config.get('schematic_command', "schematic")
schematic_folder = config.get('schematic_folder', None)
