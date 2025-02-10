import socket


class Client:
    def __init__(self):
        self._port = 3301
        self._socket = socket.socket()

    def connect(self):
        self._socket.connect(('localhost', self._port))
        print('C: ', self._socket.recv(1024))
        self._socket.close()
