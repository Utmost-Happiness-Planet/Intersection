import asyncio
import contextlib
import json
from asyncio import coroutines
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
        self.count = 0
        if isinstance(self.driver, ReverseDriver):
            name = self.get_name()
            ws_setup = WebSocketServerSetup(URL(f'/{name}'), name, self._handle_ws)
            self.setup_websocket_server(ws_setup)

    @classmethod
    @overrides(BaseAdapter)
    def get_name(cls) -> str:
        '''适配器名称: `MCDR`'''
        return 'MCDR'

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        ...

    async def heartbeat(self) -> Any:
        while True:
            await asyncio.sleep(1)
            self.count -= 1

    async def _handle_ws(self, websocket: WebSocket) -> None:
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
            self.bot_connect(bot)
            log('INFO', f'<y>Bot {escape_name}</y> connected')
            asyncio.create_task(self.heartbeat())
            self.count = 10
            try:
                while self.count > 0:
                    data = json.loads(await websocket.receive())
                    if data['type'] == 'heartbeat':
                        log('INFO', f'<y>Ping</y>')
                        await websocket.send(json.dumps({"type": "heartbeat", "value": "pong"}))
                        self.count = 10
                    elif event := Event.parse_obj(data):
                        log('INFO', f'<y>Event</y> {event}')
                        asyncio.create_task(handle_event(bot, event))
            except WebSocketClosed as e:
                log('WARNING', f'WebSocket for Bot {escape_name} closed by peer')
            except Exception as e:
                log(
                    'ERROR',
                    '<r><bg #f8bbd0>Error while process data from websocket '
                    f'for bot {escape_name}.</bg #f8bbd0></r>',
                    e,
                )
            finally:
                with contextlib.suppress(Exception):
                    await websocket.close()
                self.con_map.pop(server_name, None)
                self.bot_disconnect(bot)