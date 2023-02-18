import asyncio
import ctypes
import re

from mcdreforged.api.all import *
from nonebot_client.client import main, q

nonebot_thread: FunctionThread = None


@new_thread('nonebot')
def start(server: PluginServerInterface):
    try:
        asyncio.run(main(server))
    except:
        server.logger.info('nonebot客户端已停止')


def on_load(server: PluginServerInterface, old):
    global nonebot_thread
    nonebot_thread = start(server)
    server.logger.info('nonebot客户端已启动')


def on_info(server: PluginServerInterface, info: Info):
    if info.is_from_console:
        return
    type = ''
    name = ''
    if info.is_player:
        type = 'player'
        name = info.player
    elif info.is_from_server:
        type = 'server'
    q.put({'type': type, 'event_type': 'message', 'name': name, 'msg': info.content})
    if not info.is_user and re.fullmatch(r'Starting Minecraft server on \S*', info.content):
        server.logger.info('Minecraft is starting at address {}'.format(
            info.content.rsplit(' ', 1)[1]))


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
    server.logger.info('再见~')


def on_player_joined(server: PluginServerInterface, player, info: Info):
    ...


def on_player_left(server: PluginServerInterface, message):
    ...


def on_server_startup(server: PluginServerInterface):
    ...


def on_server_stop(server: PluginServerInterface, code):
    ...
