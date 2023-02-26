import asyncio
import ctypes
import time

from mcdreforged.api.all import *
from nonebot_client.client import data, main, online, q

nonebot_thread: FunctionThread = None


@new_thread('nonebot')
def start(server: PluginServerInterface):
    global nonebot_thread
    try:
        asyncio.run(main(server))
    except:
        server.logger.info('nonebot客户端已停止')
        return
    nonebot_thread = None
    server.logger.info('nonebot客户端已关闭')
    server.unload_plugin("nonebot_client")


def __root_command(source: InfoCommandSource):
    msg = RTextList('§6------ §cMCDR NoneBot Client§6 ------§r\n', '命令列表如下:\n')
    source.reply(msg)


def __bind_command(source: InfoCommandSource, args: dict):
    name = source.get_info().player
    user_id = args['user_id']
    if data['user_id_list'].get(user_id, None):
        source.reply(f'{user_id} 已经被 {data["user_id_list"][user_id]} 绑定！如需重新绑定请联系他进行解绑。')
    else:
        source.reply(f'{user_id} -> {name}')
        data['user_id_list'][user_id] = name
        q.put({
            'type': 'info',
            'event_type': 'message',
            'name': '通知',
            'private': False,
            'msg': f'{user_id} 已绑定至 {name}'
        })


def __reload_command(source: InfoCommandSource):
    global data
    data.clear()
    data.update(source.get_server().as_plugin_server_interface().load_config_simple(
        default_config={'user_id_list': {}}))
    source.reply('配置文件已重载')


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
    builder.command('!!nonebot reload', __reload_command)
    builder.command('!!nonebot dbg <info>', __data_command)
    builder.command('!!nonebot <user_id>', __bind_command)
    builder.arg('user_id', Text)
    builder.arg('info', Text)
    builder.register(server)

    data.update(
        server.load_config_simple(default_config={
            'url': 'ws://localhost:8080/MCDR',
            'user_id_list': {}
        }))
    if old is not None:
        online.update(old.client.online)
    nonebot_thread = start(server)
    server.logger.info('nonebot客户端已启动')
    q.put({
        'type': 'server',
        'event_type': 'message',
        'private': True,
        'name': 'server',
        'msg': 'nonebot客户端已启动'
    })


def on_info(server: PluginServerInterface, info: Info):
    if info.is_from_console or info.content.startswith('!!'):
        return
    type = ''
    name = ''
    private = False
    if info.is_player:
        type = 'player'
        name = info.player
    elif info.is_from_server:
        type = 'server'
        private = True
        return
    q.put({
        'type': type,
        'event_type': 'message',
        'private': private,
        'name': name,
        'msg': info.content
    })


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
    if nonebot_thread is not None:
        server.logger.info('等待消息处理完成...')
        i = 20
        while i:
            if q.qsize() > 0:
                i -= 1
                time.sleep(0.5)
            else:
                break
        _async_raise(nonebot_thread.ident)
    server.save_config_simple(data)
    server.logger.info('再见~')


def on_player_joined(server: PluginServerInterface, player, info: Info):
    online[player] = True
    q.put({
        'type': 'player_joined',
        'event_type': 'message',
        'private': False,
        'name': player,
        'msg': '在肝了~'
    })


def on_player_left(server: PluginServerInterface, message):
    online[message] = False
    q.put({
        'type': 'player_left',
        'event_type': 'message',
        'private': False,
        'name': message,
        'msg': '摸鱼了~'
    })


def on_server_startup(server: PluginServerInterface):
    q.put({
        'type': 'server_startup',
        'event_type': 'message',
        'private': False,
        'name': '',
        'msg': '起床啦！快来肝我~'
    })


def on_server_stop(server: PluginServerInterface, code):
    q.put({
        'type': 'server_stop',
        'event_type': 'message',
        'private': False,
        'name': code,
        'msg': '睡觉了，休息一下~ 状态码:'
    })
