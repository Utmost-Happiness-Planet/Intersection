from nonebot.adapters import Message
from nonebot.params import EventMessage
from nonebot.plugin import on_message

echo = on_message()


@echo.handle()
async def handle_echo(message: Message = EventMessage()):
    # async def handle_echo(message: Message = CommandArg()):
    print(message)
    await echo.send(message=message)
