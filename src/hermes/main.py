import asyncio
import logging

from hermes.core.DHT import DHT
from hermes.core.Storage import Storage
from hermes.net.UDPProtocol import UDPProtocol

logging.basicConfig(level=logging.INFO)

async def main():
    # US
    protocol = UDPProtocol("me", 0)
    dht = DHT(65535, protocol, Storage(), ("127.0.0.1", 3301))
    task1 = asyncio.create_task(dht.start())

    # IP:PORT used by DHT1 to send RPC
    protocol2 = UDPProtocol("127.0.0.1", 3302)
    store2 = Storage()
    store2.set(1, "joe", 1000)
    dht2 = DHT(65536, protocol2, store2, ("127.0.0.1", 3302))
    task2 = asyncio.create_task(dht2.start())

    await asyncio.sleep(2)

    await dht.bootstrap(dht2.router.node.our_contact)
    found, contacts, val = await dht.find_value(1)
    print(found, contacts, val)
    await dht.stop()
    await dht2.stop()
    # task1.cancel()
    # task2.cancel()


if __name__ == "__main__":
    asyncio.run(main())

