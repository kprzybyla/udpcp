__all__ = [
    'MessageType',
]

import enum


class MessageType(enum.IntEnum):

    Data = 1
    Ack = 2

    @classmethod
    def from_int(cls, value: int):

        return cls(value)
