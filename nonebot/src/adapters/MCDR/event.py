from pydantic import BaseModel

from nonebot.adapters import Event as BaseEvent

from .message import Message


class Event(BaseEvent):

    type: str
    event_type: str
    name: str
    private: bool
    msg: Message

    def get_type(self) -> str:
        return self.event_type

    def get_event_name(self) -> str:
        return self.name

    def get_event_description(self) -> str:
        return str(self.dict())

    def get_message(self) -> Message:
        return self.msg

    def get_plaintext(self) -> str:
        return str(self.msg)

    def get_user_id(self) -> str:
        return self.name

    def get_session_id(self) -> str:
        return self.name

    def is_tome(self) -> bool:
        return False
