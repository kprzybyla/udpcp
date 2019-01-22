__all__ = [
    'from_bytes',
    'as_bytes',
]

import bitarray
import itertools

from typing import Any, Dict, NamedTuple, Generator, Iterable

from . import exceptions

RawPacket = NamedTuple('packet', (
    ('checksum', int),
    ('message_type', int),
    ('version', int),
    ('nbit', bool),
    ('cbit', bool),
    ('sbit', bool),
    ('dbit', bool),
    ('reserved', int),
    ('fragment_amount', int),
    ('fragment_number', int),
    ('message_id', int),
    ('message_data_length', int),
    ('payload_data', bytes),
))

PACKET_FORMAT = {
    'checksum': 32,
    'message_type': 2,
    'version': 3,
    'nbit': 1,
    'cbit': 1,
    'sbit': 1,
    'dbit': 1,
    'reserved': 7,
    'fragment_amount': 8,
    'fragment_number': 8,
    'message_id': 16,
    'message_data_length': 16,
}

HEADER_SIZE = int(sum(PACKET_FORMAT.values()) / 8)


def _bits_as_int(bits: Iterable[bool], length: int) -> int:
    value = ''

    for bit in itertools.islice(bits, length):
        value += str(int(bit))

    return int(value, base=2)


def _bytes_as_ints(data: bytes, offsets: Iterable[int]) -> Generator[int, None, None]:
    bits = bitarray.bitarray()
    bits.frombytes(data)

    bits_iterator = iter(bits)

    for offset in offsets:
        yield _bits_as_int(bits_iterator, offset)


def from_bytes(data: bytes) -> RawPacket:
    if len(data) < HEADER_SIZE:
        raise exceptions.PacketInvalidHeaderLengthError(len(data), HEADER_SIZE)

    values = _bytes_as_ints(data[:HEADER_SIZE], PACKET_FORMAT.values())

    arguments: Dict[str, Any] = dict(zip(PACKET_FORMAT.keys(), values))
    arguments['nbit'] = bool(arguments['nbit'])
    arguments['cbit'] = bool(arguments['cbit'])
    arguments['sbit'] = bool(arguments['sbit'])
    arguments['dbit'] = bool(arguments['dbit'])
    arguments['payload_data'] = data[HEADER_SIZE:]

    return RawPacket(**arguments)


def as_bytes(packet) -> bytes:
    bits = bitarray.bitarray()

    for name, length in PACKET_FORMAT.items():
        value = getattr(packet, name)

        for bit in f'{value:0{length}b}':
            bits.append(int(bit))

    return bits.tobytes() + packet.payload_data
