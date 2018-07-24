__all__ = [
    'ChecksumMode',
]

import enum


class ChecksumMode(enum.IntEnum):

    Disabled = 0
    Enabled = 1

    @classmethod
    def from_bits(cls, cbit: bool):

        return cls(cbit)

    @property
    def cbit(self) -> bool:

        return bool(self.value)
