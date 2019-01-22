__all__ = [
    'PacketError',
    'PacketInvalidVersionError',
    'PacketInvalidChecksumError',
    'PacketInvalidMessageIdError',
    'PacketInvalidFragmentAmountError',
    'PacketInvalidFragmentNumberError',
    'PacketAckBasePacketError',
]

from .. import protocol


class PacketError(ValueError):
    pass


class PacketInvalidHeaderLengthError(PacketError):

    def __init__(self, length: int, header_length: int):
        super().__init__(f'Invalid packet header length {length} '
                         f'(header length: {header_length})')


class PacketInvalidVersionError(PacketError):

    def __init__(self, version: int, protocol_version: int) -> None:
        super().__init__(f'Invalid packet protocol version {version} '
                         f'(protocol version: {protocol_version})')


class PacketInvalidChecksumError(PacketError):

    def __init__(self, checksum: int, packet_checksum: int):
        super().__init__(f'Invalid packet checksum 0x{checksum:08x} '
                         f'(packet checksum: 0x{packet_checksum:08x})')


class PacketInvalidMessageIdError(PacketError):

    def __init__(self, message_id: int):
        super().__init__(f'Invalid packet message id 0x{message_id:04x}')


class PacketInvalidFragmentAmountError(PacketError):

    def __init__(self, amount: int):
        super().__init__(f'Invalid packet fragment amount {amount}')


class PacketInvalidFragmentNumberError(PacketError):

    def __init__(self, amount: int, number: int):
        super().__init__(f'Invalid packet fragment number {number} '
                         f'(fragment amount: {amount}')


class PacketAckBasePacketError(PacketError):

    def __init__(self, packet: 'protocol.Packet'):
        super().__init__(f'Invalid ack base packet {packet}')
