from typing import Iterable, Type, Union

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from nonebot.typing import overrides


class MessageSegment(BaseMessageSegment):

    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @overrides(BaseMessageSegment)
    def __str__(self) -> str:
        # process special types
        if self.is_text():
            return f"{self.data.get('text', '')}"
        return f"[{self.type}]"

    __repr__ = __str__

    @overrides(BaseMessageSegment)
    def __add__(self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]) -> "Message":
        return Message(self) + (MessageSegment.text(other) if isinstance(other, str) else other)

    __radd__ = __add__

    @overrides(BaseMessageSegment)
    def is_text(self) -> bool:
        return self.type == "text"

    @staticmethod
    def text(text: str) -> "MessageSegment":
        return MessageSegment("text", {"text": text})


class Message(BaseMessage[MessageSegment]):

    @classmethod
    @overrides(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @overrides(BaseMessage)
    def __add__(self, other: Union[str, MessageSegment, Iterable[MessageSegment]]) -> "Message":
        return super(Message,
                     self).__add__(MessageSegment.text(other) if isinstance(other, str) else other)

    def __repr__(self) -> str:
        return "".join(repr(seg) for seg in self)

    @overrides(BaseMessage)
    def __radd__(self, other: Union[str, MessageSegment, Iterable[MessageSegment]]) -> "Message":
        return super(
            Message,
            self).__radd__(MessageSegment.text(other) if isinstance(other, str) else other)

    @overrides(BaseMessage)
    def __iadd__(self, other: Union[str, MessageSegment, Iterable[MessageSegment]]) -> "Message":
        return super().__iadd__(MessageSegment.text(other) if isinstance(other, str) else other)

    @staticmethod
    @overrides(BaseMessage)
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield MessageSegment("text", {"text": msg})
