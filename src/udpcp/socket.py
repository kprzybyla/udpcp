import math
import queue
import socket as native_socket
import selectors
import threading

from typing import Dict, List, Tuple, Iterable, Optional
from collections import defaultdict

from .protocol import Packet, TransferMode, ChecksumMode

from . import exceptions
from .utils import Identifier, get_best_selector_class
from .socket_fd import SocketFileDescriptor

SocketAddress = Tuple[str, int]


class Socket:

    __slots__ = (
        '_local_address',
        '_transfer_mode',
        '_checksum_mode',
        '_retransmission_timeout',
        '_retransmission_attempts',
        '_maximum_connections',
        '_socket',
        '_thread',
        '_identifiers',
        '_outgoing_ack',
        '_outgoing_packet',
        '_incoming_data',
        '_incoming_fragments',
        '_shutdown_event',
        '_shutdown_trigger',
        '_file_descriptor',
    )

    MTU = 65536

    def __init__(
        self,
        local_address: SocketAddress = ('0.0.0.0', 0),
        transfer_mode: TransferMode = TransferMode.AckEveryPacket,
        checksum_mode: ChecksumMode = ChecksumMode.Enabled,
        *,
        retransmission_timeout: int = 100,
        retransmission_attempts: int = 5,
        maximum_connections: int = 5
    ):
        self._local_address = local_address
        self._transfer_mode = transfer_mode
        self._checksum_mode = checksum_mode
        self._retransmission_timeout = retransmission_timeout
        self._retransmission_attempts = retransmission_attempts
        self._maximum_connections = maximum_connections

        self._socket: Optional[native_socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._identifiers: Dict[SocketAddress, Identifier] = defaultdict(Identifier)
        self._outgoing_ack = threading.Event()
        self._outgoing_packet: Optional[Tuple[Packet, SocketAddress]] = None
        self._incoming_data: queue.Queue = queue.Queue()
        self._incoming_fragments: Dict[SocketAddress, List[bytes]] = defaultdict(list)

        self._shutdown_event = threading.Event()
        self._shutdown_trigger = False
        self._file_descriptor = SocketFileDescriptor()

    def __enter__(self) -> 'Socket':
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        self.close()

    def __repr__(self) -> str:
        return f'{type(self).__name__}[{self.local_address}]'

    @staticmethod
    def create_socket(reuse_address: bool = True, reuse_port: bool = True) -> native_socket.socket:
        socket = native_socket.socket(native_socket.AF_INET, native_socket.SOCK_DGRAM)

        socket.setsockopt(native_socket.SOL_SOCKET, native_socket.SO_REUSEADDR, reuse_address)
        socket.setsockopt(native_socket.SOL_SOCKET, native_socket.SO_REUSEPORT, reuse_port)

        return socket

    @property
    def is_opened(self) -> bool:
        return True if self._socket is not None else False

    @property
    def is_closed(self) -> bool:
        return not self.is_opened

    @property
    def local_address(self) -> SocketAddress:
        return self._socket.getsockname() if self._socket else self._local_address

    def fileno(self) -> int:
        return self._file_descriptor.fileno()

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        if self.is_closed:
            raise exceptions.SocketClosedError()

        self._shutdown_event.clear()

        try:
            self._serve_forever(poll_interval)
        finally:
            self._shutdown_trigger = False
            self._shutdown_event.set()

    def open(self) -> None:
        self._socket = self.create_socket()

        try:
            self._socket.bind(self._local_address)
        except native_socket.error as error:
            try:
                raise error
            finally:
                self.close()

        self._thread = threading.Thread(target=self.serve_forever)
        self._thread.start()

    def close(self) -> None:
        self.shutdown()

        if self._socket:
            self._socket.close()

        if self._thread:
            self._thread.join()

        self._socket = None

    def shutdown(self) -> None:
        self._shutdown_trigger = True
        self._shutdown_event.wait()

    def send_to(self, data: bytes, address: SocketAddress) -> None:
        if self.is_closed:
            raise exceptions.SocketClosedError()

        self._send_data(data, address)

    def receive_from(self) -> Tuple[bytes, SocketAddress]:
        try:
            return self._incoming_data.get()
        finally:
            self._file_descriptor.notify_read()

    def _serve_forever(self, poll_interval: float = 0.5) -> None:
        if not self._socket:
            raise exceptions.SocketError()

        selector_class = get_best_selector_class()
        selector = selector_class()
        selector.register(self._socket, selectors.EVENT_READ)

        while not self._shutdown_trigger:
            if selector.select(poll_interval):
                self._process_packet()

    def _send_ack(self, data: Packet, address: SocketAddress, is_duplicate: bool = False) -> None:
        ack = Packet.ack(data, is_duplicate=is_duplicate)

        if not self._socket:
            raise exceptions.SocketError()

        self._socket.sendto(ack.as_bytes, address)

    def _send_sync(self, address: SocketAddress) -> None:
        sync = Packet.sync(self._checksum_mode)

        if not self._socket:
            raise exceptions.SocketError()

        self._socket.sendto(sync.as_bytes, address)

    def _send_data(self, data: bytes, address: SocketAddress) -> None:
        message_id = self._identifiers[address].next()

        for packet in self._fragment_into_packets(message_id, data):
            for _ in range(self._retransmission_attempts):
                try:
                    self._send_data_packet(packet, address)
                except TimeoutError:
                    continue
                else:
                    break
            else:
                raise exceptions.SocketAckError()

    def _send_data_packet(self, data: Packet, address: SocketAddress) -> None:
        if data.is_ack_needed:
            self._outgoing_packet = data, address

        if not self._socket:
            raise exceptions.SocketError()

        self._socket.sendto(data.as_bytes, address)

        if data.is_ack_needed:
            self._outgoing_ack.wait(timeout=self._retransmission_timeout)
            self._outgoing_ack.clear()
            self._outgoing_packet = None

    def _fragment_into_packets(self, message_id: int, data: bytes) -> Iterable[Packet]:
        fragment_amount = int(math.ceil(len(data) / self.MTU))

        for fragment_number in range(fragment_amount):
            start = fragment_number * self.MTU
            finish = (fragment_number + 1) * self.MTU

            yield Packet.data(
                transfer_mode=self._transfer_mode,
                checksum_mode=self._checksum_mode,
                fragment_amount=fragment_amount,
                fragment_number=fragment_number,
                message_id=message_id,
                payload_data=data[start:finish],
            )

    def _process_packet(self) -> None:
        if not self._socket:
            raise exceptions.SocketError()

        data, address = self._socket.recvfrom(self.MTU)
        packet = Packet.from_bytes(data)

        if packet.is_ack:
            self._process_ack(packet, address)
        elif packet.is_sync:
            self._process_sync(packet, address)
        elif packet.is_data:
            self._process_data(packet, address)
        else:
            raise exceptions.SocketPacketError()

    def _process_ack(self, ack: Packet, address: SocketAddress) -> None:
        if self._outgoing_packet is None:
            raise exceptions.SocketAckError()

        data_packet, data_address = self._outgoing_packet

        if ack.is_ack_for(data_packet) and address == data_address:
            self._outgoing_ack.set()

    def _process_sync(self, sync: Packet, address: SocketAddress) -> None:
        self._send_ack(sync, address)

    def _process_data(self, data: Packet, address: SocketAddress) -> None:
        self._send_ack(data, address)
        self._incoming_fragments[address].append(data.payload_data)

        if len(self._incoming_fragments[address]) == data.fragment_amount:
            try:
                self._incoming_data.put((b''.join(self._incoming_fragments[address]), address))
                self._file_descriptor.notify_write()
            finally:
                del self._incoming_fragments[address]
