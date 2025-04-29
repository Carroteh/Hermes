import asyncio
import logging
import threading
import os
import datetime
import random

from hermes.core.KeyValues import LightWeightMessage
from hermes.kademlia.Contact import Contact
from hermes.kademlia.DHT import DHT
from hermes.core.Error import Error
from hermes.kademlia.Storage import Storage
from hermes.net.UDPProtocol import UDPProtocol
from hermes.core.Hermes import Hermes

# Configure the logging
logging.basicConfig(
    filename='src/hermes/logs/hermes.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def full_run():
    print_logo()

    # Setup this node
    protocol = UDPProtocol("0.0.0.0", 0)
    id = random.randint(0, 2 ** 160)
    dht = DHT(id, protocol, Storage(), ("0.0.0.0", 0))
    asyncio.create_task(dht.start())
    hermes = Hermes(dht)

    # Use asyncio.Queue for commands
    command_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def input_thread():
        while True:
            cmd = input().strip()
            loop.call_soon_threadsafe(command_queue.put_nowait, cmd)
            if cmd == "q":
                break

    threading.Thread(target=input_thread, daemon=True).start()

    # Command handler loop
    while True:
        print("> ", end="", flush=True)
        command = await command_queue.get()
        args = command.split(" ")

        if args[0] == "bootstrap":
            if len(args) != 4:
                print("usage: bootstrap <id> <host> <port>")
                continue
            await bootstrap(dht, int(args[1]), args[2], int(args[3]))
        elif args[0] == "register":
            if len(args) != 2:
                print("usage: register <nickname>")
                continue
            await register(hermes, args[1])
        elif args[0] == "send":
            if len(args) < 3:
                print("usage: send <nickname> <message>")
                continue
            await send(hermes, args[1], " ".join(args[2:]))
        elif args[0] == "read":
            if len(args) != 2:
                print("usage: read <nickname>")
                continue
            await read(hermes, args[1])
        elif args[0] == "logs":
            logs()
        elif args[0] == "clear":
            clear()
        elif args[0] == "me":
            me(dht, hermes)
        elif args[0] == "status":
            status(dht)
        elif args[0] == "store":
            if len(args) != 3:
                print("usage: store <key> <value>")
                continue
        elif args[0] == "help":
            help()
        elif command == "q":
            break

async def bootstrap(dht, id, host, port):
    prot = UDPProtocol(host, port)
    await dht.bootstrap(Contact(prot, id, host, port))
    print("Bootstrapped successfully.")

async def store(dht, key, value):
    await dht.store(key, value)

async def register(hermes, nickname: str):
    err = await hermes.register_nickname(nickname)

    if err.has_error():
        print(err.error_message)
    else:
        print("Registered successfully.")

async def send(hermes, nickname: str, message: str):
    err = await hermes.send_message(nickname, message)
    if err.has_error():
        print(err.error_message)
    else:
        print("Message sent successfully.")

async def read(hermes, nickname: str):
    msg: list[LightWeightMessage] = await hermes.get_messages_from_msg_box(nickname)

    sorted_msg = sorted(msg, key=lambda x: x.timestamp)
    for m in sorted_msg:
        print(f"{datetime.datetime.fromtimestamp(float(m.timestamp))} ({m.sender}): {m.message}")

def logs():
    with open("src/hermes/logs/hermes.log") as file:
        for line in (file.readlines()[-50:]):
            print(line, end='')

def me(dht: DHT, hermes: Hermes):
    print(f"{dht.contact.id} {dht.contact.host} {dht.contact.port} --- {hermes.get_nickname()}")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_logo()

def print_logo():
    print("""

    |     |   ___   ___    __ __    ___    __
    |___  |  |___  |   |  |  |  |  |___   |__
    |     |  |___  |      |  |  |  |___    __|

    """)

def status(dht: DHT):
    print("Contacts known: " + str(dht.router.node.bucket_list.get_num_contacts()))
    print("Storage size: " + str(len(dht.storage.store)))

def help():
    return(
        """
bootstrap <id> <host> <port> - bootstrap DHT
store <key> <value> - store a value in the DHT
logs
clear
me
status
        """
    )

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
