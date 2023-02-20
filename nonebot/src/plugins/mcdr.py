from nonebot import get_bot
from nonebot.adapters import Bot, Event
from nonebot.plugin import on_message

all = on_message()


@all.handle()
async def handle_all(bot: Bot, event: Event):
    print(event)
    if bot.self_id == "MCDR":
        msg = ''
        type = 'group'
        if event.private is True:
            type = ''
        if event.type == 'player':
            msg = f'<{event.get_user_id()}> {event.get_message()}'
        elif event.type == 'info' or event.type == 'dbg':
            msg = f'{event.get_user_id()}: {event.get_message()}'
        elif event.type == 'server' or event.type == 'server_startup':
            msg = event.get_message()
        elif event.type == 'player_joined' or event.type == 'player_left':
            msg = f'{event.get_user_id()}{event.get_message()}'
        elif event.type == 'server_stop':
            msg = f'{event.get_message()}{event.get_user_id()}'

        await get_bot("1875300947").call_api('send_msg',
                                             user_id=287547656,
                                             group_id=1083188592,
                                             message_type=type,
                                             message=msg)
    else:
        message = event.get_message()
        private = False
        if event.message_type == 'private':
            private = True
        print(event.dict())
        print(message[0])
        msg = str(message[0])
        api = 'send_msg'
        if msg.startswith("/nb"):
            msg = msg.split()
            if msg[1] == 'dbg':
                if event.get_user_id() != '287547656':
                    return
                api = 'dbg'
                if len(msg) > 2:
                    msg = msg[2]
                else:
                    msg = 'data'
            else:
                api = 'bind'
                msg = msg[1]
        else:
            msg = message.extract_plain_text()
        await get_bot("MCDR").call_api(api, user_id=event.user_id, message=msg, private=private)
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
