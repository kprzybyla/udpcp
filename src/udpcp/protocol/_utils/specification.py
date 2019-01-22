__all__ = [
    'from_bytes',
    'as_bytes',
]

import typing
import bitarray
import itertools

RawPacket = typing.NamedTuple('packet', (
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

bits_format = {
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

header_size = int(sum(bits_format.values()) / 8)


def _bits_as_int(bits: typing.Iterable[bool], length: int) -> int:

    value = ''

    for bit in itertools.islice(bits, length):
        value += str(int(bit))

    return int(value, base=2)


def _bytes_as_ints(data: bytes, offsets: typing.Iterable[int]) \
        -> typing.Generator[int, None, None]:

    bits = bitarray.bitarray()
    bits.frombytes(data)

    bits_iterator = iter(bits)

    for offset in offsets:
        yield _bits_as_int(bits_iterator, offset)


def from_bytes(data: bytes) -> RawPacket:

    if len(data) < header_size:
        raise ValueError(
            f'Couldn\'t decode raw packet from bytes: '
            f'invalid data length ({len(data)} < {header_size}).'
        )

    values = _bytes_as_ints(data[:header_size], bits_format.values())

    arguments: typing.Dict[str, typing.Any] = dict(zip(bits_format.keys(), values))

    arguments['nbit'] = bool(arguments['nbit'])
    arguments['cbit'] = bool(arguments['cbit'])
    arguments['sbit'] = bool(arguments['sbit'])
    arguments['dbit'] = bool(arguments['dbit'])
    arguments['payload_data'] = data[header_size:]

    return RawPacket(**arguments)


def as_bytes(packet) -> bytes:

    bits = bitarray.bitarray()

    for name, length in bits_format.items():

        value = getattr(packet, name)

        for bit in f'{value:0{length}b}':
            bits.append(int(bit))

    return bits.tobytes() + packet.payload_data
