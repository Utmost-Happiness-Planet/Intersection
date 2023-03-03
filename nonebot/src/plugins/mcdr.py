from nonebot import get_bot, get_driver
from nonebot.adapters import Bot, Event
from nonebot.plugin import on_message

all = on_message()

config = get_driver().config.dict()

st_cmd = config.get('mcdr_start_command', '/nb')
if (bot_id := config.get('mcdr_bot_id', None)) is None:
    raise Exception('[MCDR] 未发现配置项 `mcdr_bot_id`, 请填写bot的QQ账号!')
if (server_name := config.get('mcdr_server_name', None)) is None:
    raise Exception('[MCDR] 未发现配置项 `mcdr_server_name`, 请填写MCDR服务器名称!')
if (group_id := config.get('mcdr_group_id', None)) is None:
    raise Exception('[MCDR] 未发现配置项 `mcdr_group_id`, 请填写QQ群号!')
if (admin_list := config.get('mcdr_admin_id_list', None)) is None:
    raise Exception('[MCDR] 未发现配置项 `mcdr_admin_id_list`, 请填写管理员QQ号列表!')


@all.handle()
async def handle_all(bot: Bot, event: Event):
    print(event)
    if bot.self_id == server_name:
        msg = ''
        message_type = 'group'
        if event.private is True:
            message_type = ''
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

        await get_bot(str(bot_id)).call_api('send_msg',
                                            user_id=admin_list[0],
                                            group_id=group_id,
                                            message_type=message_type,
                                            message=msg)
    else:
        private = False
        if event.message_type == 'private':
            private = True
        elif event.group_id != group_id:
            return
        # print(event.dict())
        message = event.get_message()
        msg = str(message[0])
        # print(msg)
        api = 'send_msg'
        if msg.startswith(st_cmd):
            msg = msg.split()
            if msg[1] == 'dbg':
                if int(event.get_user_id()) not in admin_list:
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
