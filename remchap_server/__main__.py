import asyncio

from .networking import Listener, Client


clients: list[Client] = []


async def handle_client(client: Client) -> None:
    clients.append(client)
    # -------------------------
    buffer = bytearray()

    while client.connected:
        byte_read = await client.read(1)
        buffer.extend(byte_read)

        if buffer[-1:] == b"\n":
            for c in clients:
                await c.write(buffer)

            buffer.clear()
    # -------------------------
    clients.remove(client)


async def main() -> None:
    ip = "::1"
    port = 8080
    tasks = []

    listener = Listener(ip)
    print(f"Starting server on port {port}...")
    await listener.start_server(port)

    async for client in listener.incoming():
        task = asyncio.create_task(handle_client(client))
        tasks.append(task)

    await asyncio.gather(*tasks)


asyncio.run(main())
