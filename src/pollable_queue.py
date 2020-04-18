import queue
import socket
import os
from collections import deque


class PollableQueue(deque):
    def __init__(self, maxlen=1):
        super().__init__(maxlen=maxlen)
        self._putsocket, self._getsocket = socket.socketpair()

    def fileno(self):
        return self._getsocket.fileno()

    def put(self, item):
        super().append(item)
        self._putsocket.send(b'x')
        return

    def get(self):
        self._getsocket.recv(1)
        return super().popleft()