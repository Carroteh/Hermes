import sys
import asyncio
from net.ConnectionHandler import ConnectionHandler


if __name__ == "__main__":
    port = int(sys.argv[1])

    node = ConnectionHandler()
    asyncio.run(node.run_server(port))
