import pytest

from udpcp.protocol import Packet
from udpcp.protocol.behaviour import MessageType, ChecksumMode, TransferMode


def test_ack():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    assert packet.is_ack
    assert packet.type == 'ack'

    assert not packet.is_sync
    assert not packet.is_data


def test_sync():

    packet = Packet.sync(
        checksum_mode=ChecksumMode.Disabled,
    )

    assert packet.is_sync
    assert packet.type == 'sync'

    assert not packet.is_ack
    assert not packet.is_data


def test_data():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.is_data
    assert packet.type == 'data'

    assert not packet.is_ack
    assert not packet.is_sync


def test_invalid():

    packet = Packet(
        message_type=MessageType.Ack,
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        is_duplicate=True,
        fragment_amount=1,
        fragment_number=0,
        message_id=0,
        message_data_length=0,
        payload_data=b'dummy',
    )

    assert packet.type == 'invalid'

    assert not packet.is_ack
    assert not packet.is_sync
    assert not packet.is_data


def test_checksum_mode_enabled():

    packet = Packet.sync(
        checksum_mode=ChecksumMode.Enabled,
    )

    assert packet.checksum == 0x2960053


def test_checksum_mode_disabled():

    packet = Packet.sync(
        checksum_mode=ChecksumMode.Disabled,
    )

    assert packet.checksum == 0


def test_message_type_ack():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    assert packet.message_type is MessageType.Ack


def test_message_type_sync():

    packet = Packet.sync(
        checksum_mode=ChecksumMode.Disabled,
    )

    assert packet.message_type is MessageType.Data


def test_message_type_data():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.message_type is MessageType.Data


def test_transfer_mode_ack():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    assert packet.transfer_mode is TransferMode.AckNone
    assert not packet.is_ack_needed


def test_transfer_mode_sync():

    packet = Packet.sync(
        checksum_mode=ChecksumMode.Disabled,
    )

    assert packet.transfer_mode is TransferMode.AckEveryPacket
    assert packet.is_ack_needed


def test_transfer_mode_data_every_packet():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.transfer_mode is TransferMode.AckEveryPacket
    assert packet.is_ack_needed


def test_transfer_mode_data_last_fragment_only_when_ack_needed():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckLastFragmentOnly,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.transfer_mode is TransferMode.AckLastFragmentOnly
    assert packet.is_ack_needed


def test_transfer_mode_data_last_fragment_only_when_ack_not_needed():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckLastFragmentOnly,
        fragment_amount=10,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.transfer_mode is TransferMode.AckLastFragmentOnly
    assert not packet.is_ack_needed


def test_transfer_mode_data_none():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckNone,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.transfer_mode is TransferMode.AckNone
    assert not packet.is_ack_needed


def test_is_duplicate_ack_true():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
        is_duplicate=True,
    )

    assert packet.is_duplicate


def test_is_duplicate_ack_false():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    assert not packet.is_duplicate


def test_is_duplicate_sync():

    packet = Packet.sync(
        checksum_mode=ChecksumMode.Disabled,
    )

    assert not packet.is_duplicate


def test_is_duplicate_data():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert not packet.is_duplicate


def test_fragment_ack_single():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    assert packet.fragment_amount == 1
    assert packet.fragment_number == 0

    assert packet.is_single
    assert packet.is_last


def test_fragment_ack_multiple():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=10,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    assert packet.fragment_amount == 10
    assert packet.fragment_number == 0

    assert not packet.is_single
    assert not packet.is_last


def test_fragment_ack_multiple_last():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=10,
        fragment_number=9,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    assert packet.fragment_amount == 10
    assert packet.fragment_number == 9

    assert not packet.is_single
    assert packet.is_last


def test_fragment_sync():

    packet = Packet.sync(
        checksum_mode=ChecksumMode.Disabled,
    )

    assert packet.fragment_amount == 1
    assert packet.fragment_number == 0

    assert packet.is_single
    assert packet.is_last


def test_fragment_data_single():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.fragment_amount == 1
    assert packet.fragment_number == 0

    assert packet.is_single
    assert packet.is_last


def test_fragment_data_multiple():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=10,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.fragment_amount == 10
    assert packet.fragment_number == 0

    assert not packet.is_single
    assert not packet.is_last


def test_fragment_data_multiple_last():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=10,
        fragment_number=9,
        message_id=1,
        payload_data=b'dummy',
    )

    assert packet.fragment_amount == 10
    assert packet.fragment_number == 9

    assert not packet.is_single
    assert packet.is_last


def test_message_id_and_data_length_ack():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=12345,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    assert packet.message_id == 12345
    assert packet.message_data_length == 0


def test_message_id_and_data_length_sync():

    packet = Packet.sync(
        checksum_mode=ChecksumMode.Disabled,
    )

    assert packet.message_id == 0
    assert packet.message_data_length == 0


def test_message_id_and_data_length_data():

    packet = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=12345,
        payload_data=b'dummy',
    )

    assert packet.message_id == 12345
    assert packet.message_data_length == 5


def test_invalid_ack():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    packet = Packet.ack(
        base_packet=data,
    )

    with pytest.raises(ValueError):
        Packet.ack(
            base_packet=packet,
        )


def test_invalid_data():

    with pytest.raises(ValueError):

        Packet.data(
            checksum_mode=ChecksumMode.Disabled,
            transfer_mode=TransferMode.AckEveryPacket,
            fragment_amount=1,
            fragment_number=0,
            message_id=0,
            payload_data=b'dummy',
        )

    with pytest.raises(ValueError):

        Packet.data(
            checksum_mode=ChecksumMode.Disabled,
            transfer_mode=TransferMode.AckEveryPacket,
            fragment_amount=0,
            fragment_number=0,
            message_id=1,
            payload_data=b'dummy',
        )

    with pytest.raises(ValueError):

        Packet.data(
            checksum_mode=ChecksumMode.Disabled,
            transfer_mode=TransferMode.AckEveryPacket,
            fragment_amount=1,
            fragment_number=1,
            message_id=1,
            payload_data=b'dummy',
        )

    with pytest.raises(ValueError):

        Packet.data(
            checksum_mode=ChecksumMode.Disabled,
            transfer_mode=TransferMode.AckEveryPacket,
            fragment_amount=1,
            fragment_number=-1,
            message_id=1,
            payload_data=b'dummy',
        )


def test_encode_decode_ack():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=10,
        fragment_number=5,
        message_id=12345,
        payload_data=b'dummy',
    )

    encoded = Packet.ack(
        base_packet=data,
    )

    encoded_bytes = bytes(encoded)

    decoded = Packet.from_bytes(encoded_bytes)
    decoded_bytes = decoded.as_bytes

    assert encoded_bytes == decoded_bytes


def test_encode_decode_ack_duplicate():

    data = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=10,
        fragment_number=5,
        message_id=12345,
        payload_data=b'dummy',
    )

    encoded = Packet.ack(
        base_packet=data,
        is_duplicate=True,
    )

    encoded_bytes = bytes(encoded)

    decoded = Packet.from_bytes(encoded_bytes)
    decoded_bytes = decoded.as_bytes

    assert encoded_bytes == decoded_bytes


def test_encode_decode_sync_checksum_mode_enabled():

    encoded = Packet.sync(
        checksum_mode=ChecksumMode.Enabled,
    )

    encoded_bytes = bytes(encoded)

    decoded = Packet.from_bytes(encoded_bytes)
    decoded_bytes = decoded.as_bytes

    assert encoded_bytes == decoded_bytes


def test_encode_decode_sync_checksum_mode_disabled():

    encoded = Packet.sync(
        checksum_mode=ChecksumMode.Disabled,
    )

    encoded_bytes = bytes(encoded)

    decoded = Packet.from_bytes(encoded_bytes)
    decoded_bytes = decoded.as_bytes

    assert encoded_bytes == decoded_bytes


def test_encode_decode_data():

    encoded = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckEveryPacket,
        fragment_amount=10,
        fragment_number=5,
        message_id=12345,
        payload_data=b'dummy',
    )

    encoded_bytes = bytes(encoded)

    decoded = Packet.from_bytes(encoded_bytes)
    decoded_bytes = decoded.as_bytes

    assert encoded_bytes == decoded_bytes


def test_encode_decode_data_ack_last_fragment_only():

    encoded = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckLastFragmentOnly,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    encoded_bytes = bytes(encoded)

    decoded = Packet.from_bytes(encoded_bytes)
    decoded_bytes = decoded.as_bytes

    assert encoded_bytes == decoded_bytes


def test_decode_invalid_data_length():

    with pytest.raises(ValueError):
        Packet.from_bytes(b'dummy')


def test_decode_invalid_packet_protocol_version():

    with pytest.raises(ValueError):
        Packet.from_bytes(b'000000000000')


def test_decode_invalid_packet_checksum():

    encoded = Packet.data(
        checksum_mode=ChecksumMode.Disabled,
        transfer_mode=TransferMode.AckLastFragmentOnly,
        fragment_amount=1,
        fragment_number=0,
        message_id=1,
        payload_data=b'dummy',
    )

    encoded._checksum = 12345

    with pytest.raises(ValueError):
        Packet.from_bytes(bytes(encoded))
