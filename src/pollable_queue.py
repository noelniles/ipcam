import queue
import socket
import os


class PollableQueue(queue.Queue):
    def __init__(self, maxsize=10):
        super().__init__(maxsize=maxsize)
        self._putsocket, self._getsocket = socket.socketpair()

    def fileno(self):
        return self._getsocket.fileno()

    def put(self, item):
        super().put(item)
        self._putsocket.send(b'x')

    def get(self):
        self._getsocket.recv(1)
        return super().get()