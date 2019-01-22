__all__ = [
    'TransferMode',
]

import enum


class TransferMode(enum.IntEnum):

    AckEveryPacket = 0
    AckLastFragmentOnly = 1
    AckNone = 2

    @classmethod
    def from_bits(cls, nbit: bool, sbit: bool):

        if nbit:
            return cls.AckNone
        elif sbit:
            return cls.AckLastFragmentOnly
        else:
            return cls.AckEveryPacket

    @property
    def nbit(self) -> bool:

        if self is self.AckNone:
            return True
        elif self is self.AckLastFragmentOnly:
            return False
        else:
            return False

    @property
    def sbit(self) -> bool:

        if self is self.AckNone:
            return False
        elif self is self.AckLastFragmentOnly:
            return True
        else:
            return False
