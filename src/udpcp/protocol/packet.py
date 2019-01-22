__all__ = [
    'Packet',
]

import zlib

from . import exceptions
from .packet_type import PacketType
from .message_type import MessageType
from .transfer_mode import TransferMode
from .checksum_mode import ChecksumMode

from . import _specification


class Packet:

    version = 2

    __slots__ = (
        '_checksum',
        '_message_type',
        '_transfer_mode',
        '_checksum_mode',
        '_is_duplicate',
        '_fragment_amount',
        '_fragment_number',
        '_message_id',
        '_message_data_length',
        '_payload_data',
    )

    def __init__(
        self,
        message_type: MessageType,
        transfer_mode: TransferMode,
        checksum_mode: ChecksumMode,
        is_duplicate: bool,
        fragment_amount: int,
        fragment_number: int,
        message_id: int,
        message_data_length: int,
        payload_data: bytes,
    ) -> None:
        self._checksum = 0
        self._message_type = message_type
        self._transfer_mode = transfer_mode
        self._checksum_mode = checksum_mode
        self._is_duplicate = is_duplicate
        self._fragment_amount = fragment_amount
        self._fragment_number = fragment_number
        self._message_id = message_id
        self._message_data_length = message_data_length
        self._payload_data = payload_data

        self._calculate_checksum()

    def __repr__(self):
        return ''.join([
            'udpcp.protocol.Packet[',
            f'type = {self.type.value}, ',
            f'version = {self.version}, ',
            f'checksum = 0x{self.checksum:08x}, ',
            f'checksum_mode = {self.checksum_mode}, ',
            f'transfer_mode = {self.transfer_mode}, ',
            f'fragment_amount = {self.fragment_amount}, ',
            f'fragment_number = {self.fragment_number}, ',
            f'message_id = 0x{self.message_id:04x}, ',
            f'message_data_length = {self.message_data_length}, ',
            f'payload_data = {self.payload_data}',
            ']',
        ])

    def __bytes__(self):
        return self.as_bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Packet':
        raw = _specification.from_bytes(data)

        if raw.version != cls.version:
            raise exceptions.PacketInvalidVersionError(raw.version, cls.version)

        packet = cls(
            MessageType.from_int(raw.message_type),
            TransferMode.from_bits(raw.nbit, raw.sbit),
            ChecksumMode.from_bits(raw.cbit),
            raw.dbit,
            raw.fragment_amount,
            raw.fragment_number,
            raw.message_id,
            raw.message_data_length,
            raw.payload_data,
        )

        if raw.checksum != packet.checksum:
            raise exceptions.PacketInvalidChecksumError(raw.checksum, packet.checksum)

        return packet

    @classmethod
    def ack(cls, base_packet: 'Packet', is_duplicate: bool = False) -> 'Packet':
        if not base_packet.is_data and not base_packet.is_sync:
            raise exceptions.PacketAckBasePacketError(base_packet)

        return cls(
            message_type=MessageType.Ack,
            transfer_mode=TransferMode.AckNone,
            checksum_mode=base_packet.checksum_mode,
            is_duplicate=is_duplicate,
            fragment_amount=base_packet.fragment_amount,
            fragment_number=base_packet.fragment_number,
            message_id=base_packet.message_id,
            message_data_length=0,
            payload_data=b'',
        )

    @classmethod
    def sync(cls, checksum_mode: ChecksumMode) -> 'Packet':
        return cls(
            message_type=MessageType.Data,
            transfer_mode=TransferMode.AckEveryPacket,
            checksum_mode=checksum_mode,
            is_duplicate=False,
            fragment_amount=1,
            fragment_number=0,
            message_id=0,
            message_data_length=0,
            payload_data=b'',
        )

    @classmethod
    def data(
        cls,
        transfer_mode: TransferMode,
        checksum_mode: ChecksumMode,
        fragment_amount: int,
        fragment_number: int,
        message_id: int,
        payload_data: bytes,
    ) -> 'Packet':
        if message_id == 0:
            raise exceptions.PacketInvalidMessageIdError(message_id)

        if fragment_amount < 1:
            raise exceptions.PacketInvalidFragmentAmountError(fragment_amount)

        if fragment_number < 0:
            raise exceptions.PacketInvalidFragmentNumberError(fragment_amount, fragment_number)

        if fragment_number >= fragment_amount:
            raise exceptions.PacketInvalidFragmentNumberError(fragment_amount, fragment_number)

        return cls(
            message_type=MessageType.Data,
            transfer_mode=transfer_mode,
            checksum_mode=checksum_mode,
            is_duplicate=False,
            fragment_amount=fragment_amount,
            fragment_number=fragment_number,
            message_id=message_id,
            message_data_length=len(payload_data),
            payload_data=payload_data,
        )

    @property
    def type(self) -> PacketType:
        if self.is_ack:
            return PacketType.Ack
        elif self.is_sync:
            return PacketType.Sync
        elif self.is_data:
            return PacketType.Data
        else:
            return PacketType.Invalid

    @property
    def message_type(self) -> MessageType:
        return self._message_type

    @property
    def checksum(self) -> int:
        return self._checksum

    @property
    def transfer_mode(self) -> TransferMode:
        return self._transfer_mode

    @property
    def checksum_mode(self) -> ChecksumMode:
        return self._checksum_mode

    @property
    def nbit(self) -> bool:
        return self.transfer_mode.nbit

    @property
    def cbit(self) -> bool:
        return self.checksum_mode.cbit

    @property
    def sbit(self) -> bool:
        return self.transfer_mode.sbit

    @property
    def dbit(self) -> bool:
        return self.is_duplicate

    @property
    def is_duplicate(self) -> bool:
        return self._is_duplicate

    @property
    def reserved(self) -> int:
        return 0

    @property
    def fragment_amount(self) -> int:
        return self._fragment_amount

    @property
    def fragment_number(self) -> int:
        return self._fragment_number

    @property
    def message_id(self) -> int:
        return self._message_id

    @property
    def message_data_length(self) -> int:
        return self._message_data_length

    @property
    def payload_data(self) -> bytes:
        return self._payload_data

    @property
    def is_ack(self) -> bool:
        return (
            MessageType.Ack is self.message_type
            and TransferMode.AckNone is self.transfer_mode
            and self.message_data_length == 0
        )

    @property
    def is_sync(self) -> bool:
        return (
            MessageType.Data is self.message_type
            and TransferMode.AckEveryPacket is self.transfer_mode
            and not self.is_duplicate
            and self.message_id == 0
            and self.message_data_length == 0
        )

    @property
    def is_data(self) -> bool:
        return (
            MessageType.Data is self.message_type
            and not self.is_duplicate
            and self.message_id != 0
        )

    @property
    def is_single(self) -> bool:
        return (
            self.fragment_amount == 1
            and self.fragment_number == 0
        )

    @property
    def is_last(self) -> bool:
        return self.fragment_amount == self.fragment_number + 1

    @property
    def is_ack_needed(self) -> bool:
        ack_every_packet = TransferMode.AckEveryPacket is self.transfer_mode
        ack_last_fragment_only = TransferMode.AckLastFragmentOnly is self.transfer_mode

        return ack_every_packet or (ack_last_fragment_only and self.is_last)

    @property
    def as_bytes(self) -> bytes:
        return _specification.as_bytes(self)

    def is_ack_for(self, data: 'Packet') -> bool:
        return (
            self.is_ack
            and self.message_id == data.message_id
            and self.fragment_amount == data.fragment_amount
            and self.fragment_number == data.fragment_number
        )

    def _calculate_checksum(self) -> None:
        self._checksum = 0

        if self.checksum_mode is not ChecksumMode.Disabled:
            self._checksum = zlib.adler32(self.as_bytes, 1)
