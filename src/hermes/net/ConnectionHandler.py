from net.RequestHandler import RequestHandler
import asyncio


class ConnectionHandler:
    def __init__(self):
        pass

    async def run_server(self, port, /):
        print("Starting server")
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: RequestHandler(),
            local_addr=('127.0.0.1', port)
        )

        try:
            await asyncio.sleep(3600)  # Run for 1 hour
        finally:
            transport.close()
