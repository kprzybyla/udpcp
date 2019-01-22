import os
import threading


class SocketFileDescriptor:

    INPUT = b'W'

    def __init__(self):
        self._value = 0
        self._condition = threading.Condition(threading.Lock())
        self._read_fd, self._write_fd = os.pipe()

    def __del__(self):
        os.close(self._read_fd)
        os.close(self._write_fd)

    def fileno(self) -> int:
        return self._read_fd

    def notify_read(self) -> None:
        with self._condition:
            assert self._value > 0
            self._value -= 1
            self._set_event_read()

    def notify_write(self) -> None:
        with self._condition:
            self._value += 1
            self._set_event_write()

    def _set_event_read(self) -> None:
        if self._value == 0:
            assert self.INPUT == os.read(self._read_fd, len(self.INPUT))

    def _set_event_write(self) -> None:
        if self._value == 1:
            os.write(self._write_fd, self.INPUT)
