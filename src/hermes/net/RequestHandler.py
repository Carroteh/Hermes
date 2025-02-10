import asyncio


class RequestHandler(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"Received Message: {message} from: {addr}")
        self.transport.sendto(b"what do yuou want.", addr)
