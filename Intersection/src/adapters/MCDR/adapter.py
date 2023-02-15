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

log = logger_wrapper("MCDR")


class Adapter(BaseAdapter):

    @overrides(BaseAdapter)
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        if isinstance(self.driver, ReverseDriver):
            name = self.get_name()
            ws_setup = WebSocketServerSetup(URL(f'/{name}'), name, self._handle_ws)
            self.setup_websocket_server(ws_setup)

    @classmethod
    @overrides(BaseAdapter)
    def get_name(cls) -> str:
        """适配器名称: `MCDR`"""
        return "MCDR"

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        ...

    async def _handle_ws(self, websocket: WebSocket) -> None:
        await websocket.accept()
        name = self.get_name()
        escape_name = escape_tag(name)
        bot = Bot(self, name)
        self.bot_connect(bot)
        log("INFO", f"<y>Bot {escape_name}</y> connected")
        try:
            while True:
                data = await websocket.receive()
                if event := Event.parse_obj(json.loads(data)):
                    asyncio.create_task(handle_event(bot, event))
        except WebSocketClosed as e:
            log("WARNING", f"WebSocket for Bot {escape_name} closed by peer")
        except Exception as e:
            log(
                "ERROR",
                "<r><bg #f8bbd0>Error while process data from websocket "
                f"for bot {escape_name}.</bg #f8bbd0></r>",
                e,
            )
        finally:
            with contextlib.suppress(Exception):
                await websocket.close()
            self.bot_disconnect(bot)