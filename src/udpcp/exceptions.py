__all__ = [
    'SocketError',
    'SocketClosedError',
    'SocketAckError',
    'SocketPacketError',
]

import socket as native_socket


class SocketError(native_socket.error):
    pass


class SocketClosedError(SocketError):
    pass


class SocketAckError(SocketError):
    pass


class SocketPacketError(SocketError):
    pass
