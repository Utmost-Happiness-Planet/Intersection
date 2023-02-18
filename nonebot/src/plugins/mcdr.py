from nonebot import get_bot
from nonebot.adapters import Bot, Event
from nonebot.plugin import on_message

all = on_message()


@all.handle()
async def handle_echo(bot: Bot, event: Event):
    print(event)
    if bot.self_id == "MCDR":
        if event.type == 'player':
            await get_bot("1875300947").call_api(
                'send_msg',
                group_id=1083188592,
                message_type='group',
                message=f'<{event.get_user_id()}> {event.get_message()}')
    else:
        message = event.get_message()
        print(message[0])
        await get_bot("MCDR").call_api('send_msg',
                                       user_id=event.user_id,
                                       message=message.extract_plain_text())
    # a = {
    #     'time': 1676724194,
    #     'self_id': 1875300947,
    #     'post_type': 'message',
    #     'sub_type': 'normal',
    #     'user_id': 287547656,
    #     'message_type': 'group',
    #     'message_id': 2020239082,
    #     'message': 123,
    #     'original_message': 123,
    #     'raw_message': '123',
    #     'font': 0,
    #     'sender': {
    #         'user_id': 287547656,
    #         'nickname': 'MC_cube',
    #         'sex': 'unknown',
    #         'age': 0,
    #         'card': 'MC_cubes',
    #         'area': '',
    #         'level': '',
    #         'role': 'owner',
    #         'title': ''
    #     },
    #     'to_me': False,
    #     'reply': None,
    #     'group_id': 1083188592,
    #     'anonymous': None,
    #     'message_seq': 85289
    # }
