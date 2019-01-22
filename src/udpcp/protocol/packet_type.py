__all__ = [
    'PacketType',
]

import enum


class PacketType(enum.Enum):

    Ack = 'ack'
    Sync = 'sync'
    Data = 'data'
    Invalid = 'invalid'
