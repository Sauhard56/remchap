import asyncio
import os

from .networking import Client

async def handle_client_read(client: Client) -> None:
    buffer = bytearray()
    while client.connected:
        byte_read = await client.read(1)
        buffer.extend(byte_read)

        if byte_read == b"\n":
            print(buffer.decode().strip())
            buffer.clear()


async def send_messages(client: Client) -> None:
    while client.connected:
        message = await asyncio.to_thread(lambda: input("> ") + os.linesep)
        await client.write(message.encode())


async def main():
    client = Client()
    await client.connect("::1", 8080)

    read_task = handle_client_read(client)
    write_task = send_messages(client)

    await asyncio.gather(read_task, write_task)


asyncio.run(main())
