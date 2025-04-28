import asyncio
import logging
import threading
import os
import random

from hermes.core.Contact import Contact
from hermes.core.DHT import DHT
from hermes.core.Storage import Storage
from hermes.net.UDPProtocol import UDPProtocol

# Configure the logging
logging.basicConfig(
    filename='src/hermes/logs/hermes.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def bootstrap(dht, id, host, port):
    print(f"bootstrapping: {id}, {host}, {port}")
    prot = UDPProtocol(host, port)
    await dht.bootstrap(Contact(prot, id, host, port))


def logs():
    with open("src/hermes/logs/hermes.log") as file:
        for line in (file.readlines()[-50:]):
            print(line, end='')

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

async def full_run():
    print("""

    |     |   ___   ___    __ __    ___    __
    |___  |  |___  |   |  |  |  |  |___   |__
    |     |  |___  |      |  |  |  |___    __|

    """)

    protocol = UDPProtocol("127.0.0.1", 0)
    id = random.randint(0, 2 ** 160)
    dht = DHT(id, protocol, Storage(), ("127.0.0.1", 0))
    asyncio.create_task(dht.start())

    # Use asyncio.Queue for commands
    command_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def input_thread():
        while True:
            cmd = input("> ").strip()
            loop.call_soon_threadsafe(command_queue.put_nowait, cmd)
            if cmd == "q":
                break

    threading.Thread(target=input_thread, daemon=True).start()

    print("bootstrap:sender     q:QUIT")
    while True:
        command = await command_queue.get()
        args = command.split(" ")

        if args[0] == "bootstrap":
            if len(args) < 4:
                print("usage: bootstrap <id> <host> <port>")
                continue
            await bootstrap(dht, int(args[1]), args[2], int(args[3]))
            print("bootstrapped")
        elif args[0] == "logs":
            logs()
        elif args[0] == "clear":
            clear()
        elif args[0] == "me":
            print(dht.contact)
        elif command == "q":
            break

async def test_run():
    protocol = UDPProtocol("127.0.0.1", 3301)
    dht = DHT(65535, protocol, Storage(), ("127.0.0.1", 3301))
    task1 = asyncio.create_task(dht.start())

    #IP:PORT used by DHT1 to send RPC
    protocol2 = UDPProtocol("127.0.0.1", 3302)
    store2 = Storage()
    store2.set(1, "joe", 1000)
    dht2 = DHT(65536, protocol2, store2, ("127.0.0.1", 3302))
    task2 = asyncio.create_task(dht2.start())

    await asyncio.sleep(1)

    await dht.bootstrap(dht2.router.node.our_contact)
    found, contacts, val = await dht.find_value(1)
    print(found, contacts, val)
    await dht.stop()
    await dht2.stop()

async def main():
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    await full_run()







if __name__ == "__main__":
    asyncio.run(main())

