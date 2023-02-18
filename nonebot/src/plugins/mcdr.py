from nonebot import get_bot
from nonebot.adapters import Bot, Event
from nonebot.plugin import on_message

all = on_message()


@all.handle()
async def handle_echo(bot: Bot, event: Event):
    if bot.self_id == "MCDR":
        print(event)
        if event.type == 'player':
            await get_bot("1875300947").call_api(
                'send_msg',
                group_id=1083188592,
                message_type='group',
                message=f'<{event.get_user_id()}> {event.get_message()}')
    else:
        await get_bot("MCDR").call_api('send_msg', message=event.get_message())
