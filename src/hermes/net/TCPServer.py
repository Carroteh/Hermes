import zmq
import zmq.asyncio
import datetime
import logging

from hermes.core.KeyValues import LightWeightMessage, MessageValue

logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self):
        # The chat that is currently open for the user
        self._host = ''
        self._port = 0
        self._ctx = zmq.asyncio.Context()

    async def handle_requests(self, host, message_parser: callable, listening_to: list[str]):
        try:
            socket = self._ctx.socket(zmq.REP)
            self._port = socket.bind_to_random_port(f"tcp://{host}")
            self._host = host

            while True:
                msg = await socket.recv_json()
                clear_msg: LightWeightMessage = message_parser(MessageValue.from_json(msg))
                if clear_msg.sender in listening_to:
                    print(
                        f"{datetime.datetime.fromtimestamp(clear_msg.timestamp).strftime("%Y-%d-%b %H:%M")} ({clear_msg.sender}): {clear_msg.message}")

                # Always reply
                await socket.send_json({"status": "ok"})
        except Exception as e:
            logger.error(f"Error when listening: {e}")


    async def send_message(self, msg: MessageValue, host: str, port: int):
        try:
            socket = self._ctx.socket(zmq.REQ)
            socket.connect(f"tcp://{host}:{port}")
            await socket.send_json(msg.to_json())
        except Exception as e:
            logger.error(f"Error when sending message: {e}")

    @property
    def listening_to(self):
        return self._listening_to

    @listening_to.setter
    def listening_to(self, value):
        self._listening_to = value

    @property
    def port(self):
        return self._port