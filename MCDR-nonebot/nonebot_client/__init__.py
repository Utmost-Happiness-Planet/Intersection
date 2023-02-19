import asyncio
import ctypes

from mcdreforged.api.all import *
from nonebot_client.client import data, main, online, q

nonebot_thread: FunctionThread = None


@new_thread('nonebot')
def start(server: PluginServerInterface):
    try:
        asyncio.run(main(server))
    except:
        server.logger.info('nonebot客户端已停止')


def __root_command(source: InfoCommandSource):
    msg = RTextList('§6------ §cMCDR NoneBot Client§6 ------§r\n', '命令列表如下:\n')
    source.reply(msg)


def __re_command(source: InfoCommandSource, args: dict):
    name = source.get_info().player
    user_id = args['user_id']
    if data['user_id_list'].get(user_id, None):
        source.reply(f'{user_id} 已经被 {data["user_id_list"][user_id]} 绑定！如需重新绑定请联系他进行解绑。')
    else:
        source.reply(f'{user_id} -> {name}')
        data['user_id_list'][user_id] = name


def __data_command(source: InfoCommandSource, args: dict):
    if args['info'] == 'data':
        source.reply(data)
    else:
        source.reply(online)


def on_load(server: PluginServerInterface, old):
    global nonebot_thread
    global data
    global online
    builder = SimpleCommandBuilder()
    server.register_help_message('!!nonebot', 'NoneBot Client')
    builder.command('!!nonebot', __root_command)
    builder.command('!!nonebot dbg <info>', __data_command)
    builder.command('!!nonebot <user_id>', __re_command)
    builder.arg('user_id', Integer)
    builder.arg('info', Text)
    builder.register(server)

    data.update(server.load_config_simple(default_config={'user_id_list': {}}))
    if old is not None:
        data.update(old.client.data)
        online.update(old.client.online)
    server.logger.warn(data)
    nonebot_thread = start(server)
    server.logger.info('nonebot客户端已启动')
    q.put({'type': 'server', 'event_type': 'message', 'name': 'server', 'msg': 'nonebot客户端已启动'})


def on_info(server: PluginServerInterface, info: Info):
    if info.is_from_console or info.content.startswith('!!'):
        return
    type = ''
    name = ''
    if info.is_player:
        type = 'player'
        name = info.player
    elif info.is_from_server:
        type = 'server'
    q.put({'type': type, 'event_type': 'message', 'name': name, 'msg': info.content})


def _async_raise(tid) -> int:
    tid = ctypes.c_long(tid)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    return res


def on_unload(server: PluginServerInterface):
    _async_raise(nonebot_thread.ident)
    server.save_config_simple(data)
    server.logger.info('再见~')


def on_player_joined(server: PluginServerInterface, player, info: Info):
    online[player] = True
    q.put({'type': 'player_joined', 'event_type': 'message', 'name': player, 'msg': info.content})


def on_player_left(server: PluginServerInterface, message):
    online[message] = False
    q.put({'type': 'player_left', 'event_type': 'message', 'name': '', 'msg': message})


def on_server_startup(server: PluginServerInterface):
    q.put({'type': 'server_startup', 'event_type': 'message', 'name': '', 'msg': ''})


def on_server_stop(server: PluginServerInterface, code):
    q.put({'type': 'server_stop', 'event_type': 'message', 'name': '', 'msg': code})
