import socket


class Server:
    def __init__(self):
        self._port = 3301
        self._socket = socket.socket()
        self._socket.bind(('', self._port))
        self._socket.listen(5)

    def open(self):
        while True:
            c, addr = self._socket.accept()
            print('WHAAAAAAAAAAAAT>>< ', addr)
            c.send(b'HUH')
            c.close()