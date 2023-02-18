import asyncio
import contextlib
import json
from typing import Any

from nonebot.adapters import Adapter as BaseAdapter
from nonebot.drivers import (URL, Driver, ForwardDriver, HTTPServerSetup, Request, Response,
                             ReverseDriver, WebSocket, WebSocketServerSetup)
from nonebot.exception import WebSocketClosed
from nonebot.message import handle_event
from nonebot.typing import overrides
from nonebot.utils import DataclassEncoder, escape_tag, logger_wrapper

from .bot import Bot
from .config import Config
from .event import Event
from .message import Message, MessageSegment

log = logger_wrapper('MCDR')


class Adapter(BaseAdapter):

    @overrides(BaseAdapter)
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        self.con_map: dict[str, WebSocket] = {}
        if isinstance(self.driver, ReverseDriver):
            name = self.get_name()
            ws_setup = WebSocketServerSetup(URL(f'/{name}'), name, self.__handle)
            self.setup_websocket_server(ws_setup)

    @classmethod
    @overrides(BaseAdapter)
    def get_name(cls) -> str:
        '''适配器名称: `MCDR`'''
        return 'MCDR'

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        log("DEBUG", f"调用 MCDR API <y>{api}</y>")
        websocket = self.con_map.get(bot.self_id, None)
        if websocket:
            data = json.dumps({
                "action": api,
                "params": data,
            }, cls=DataclassEncoder)
            log("DEBUG", f"data <y>{data}</y>")
            await websocket.send(data)

    async def __handle(self, websocket: WebSocket) -> None:
        server_name = websocket.request.headers.get('server_name')
        if not server_name:
            log('WARNING', '请求头缺少服务名称')
            await websocket.close(1008, '请求头缺少服务名称')
        elif server_name in self.bots:
            log('WARNING', f'服务器名称 {server_name} 已被使用')
            await websocket.close(1008, f'服务器名称 {server_name} 已被使用')
        else:
            await websocket.accept()
            name = self.get_name()
            escape_name = escape_tag(name)
            bot = Bot(self, name)
            self.con_map[name] = websocket
            self.bot_connect(bot)
            log('INFO', f'<y>服务器 {escape_name}</y> 已链接')
            try:
                while True:
                    data = json.loads(await websocket.receive())
                    if data['type'] == 'heartbeat':
                        ...
                    elif event := Event.parse_obj(data):
                        asyncio.create_task(handle_event(bot, event))
            except WebSocketClosed as e:
                log('WARNING', f'服务器 {escape_name} 已断开链接')
            except Exception as e:
                log('ERROR', f'<r><bg #f8bbd0>从服务器 {escape_name} 获取数据失败</bg #f8bbd0></r>', e)
            finally:
                with contextlib.suppress(Exception):
                    await websocket.close()
                self.con_map.pop(server_name, None)
                self.bot_disconnect(bot)
