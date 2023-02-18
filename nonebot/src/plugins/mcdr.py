from nonebot import get_bot
from nonebot.adapters import Bot, Message
from nonebot.params import EventMessage
from nonebot.plugin import on_message
from nonebot.rule import to_me

all = on_message()


@all.handle()
async def handle_echo(bot: Bot, message: Message = EventMessage()):
    if bot.self_id == "MCDR":
        # await get_bot("MCDR").call_api('send_msg', message=message)
        # await echo.send(message=message)
        print(message.__repr__())
        if message['type'] == 'player':
            await get_bot("1875300947").call_api('send_msg',
                                                user_id=1875300947,
                                                group_id=1083188592,
                                                message_type='group',
                                                message=message)
    else:
        print(message.extract_plain_text())
        await get_bot("MCDR").call_api('send_msg', message=message)
