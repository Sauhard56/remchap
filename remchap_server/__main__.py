import json
import argparse
import errno
import asyncio
from typing import Iterable

from .networking import Listener, Client


client_names: dict[Client, str | None] = {}
tasks: list[asyncio.Task] = []


async def handle_client(client: Client) -> None:
    try:
        client_names[client] = None

        await client.write(b"R3MCH4P")  # Send identity

        while True:
            buffer = bytearray()
            while len(buffer) < 4:
                data = await client.read(4 - len(buffer))
                if not data:
                    return
                buffer.extend(data)

            size = int.from_bytes(buffer, "big")

            # Content too large, no need to process
            if size > 2048:
                break
            buffer.clear()

            while len(buffer) < size:
                try:
                    data = await client.read(size - len(buffer), timeout=10.0)
                    if not data:
                        return
                    buffer.extend(data)
                except TimeoutError:
                    return

            try:
                json_message = json.loads(buffer.decode())
                if not await read_message(client, json_message):
                    return
            except (UnicodeDecodeError, json.JSONDecodeError, AssertionError):
                return

    finally:
        name = client_names.get(client)
        client_names.pop(client, None)

        if name:
            await send_message(client_names, None, f"`{name}` left the chat.")
        client.close()


async def send_message(clients: Iterable[Client], name: str | None, message: str) -> None:
    json_message = json.dumps({"name": name, "message": message}).encode()

    size_bytes = len(json_message).to_bytes(4, "big")
    for client in clients:
        tasks.append(asyncio.create_task(client.write(size_bytes + json_message)))


async def read_message(client: Client, json_message: dict) -> bool:
    msg_type = json_message.get("type")

    match msg_type:
        case "message":
            message = json_message.get("message", "")

            if client_names[client] is None:
                login_command = "/login "
                if message.startswith(login_command):
                    name = message[len(login_command):].strip()
                    if not 0 < len(name) < 25:
                        await send_message((client,), None,
                                           "Name must be between 1 ~ 25 characters.")
                    elif not all(c.isalnum() or c.isspace() for c in name):
                        await send_message((client,), None,
                                           "Name cannot contain special characters.")
                    elif name in client_names.values():
                        await send_message((client,), None, "That name is already taken.")
                    else:
                        client_names[client] = name
                        await send_message((c for c, name in client_names.items() if name),
                                           None, f"`{name}` joined the chat.")
                else:
                    await send_message((client,), None,
                                       "You must login first using `/login <username>`.")
            else:
                await send_message((c for c, name in client_names.items() if name),
                                   client_names[client], message)

            return True

        case "ping":
            return True

        case _:
            return False


async def main() -> None:
    parser = argparse.ArgumentParser("remchap_server",
                                     description="Remchap (remote chat app) relay server.")
    parser.add_argument("--address", "-a", help="The ip address to listen on.", default="127.0.0.1")
    parser.add_argument("--port", "-p", help="The port to listen on.", type=int, default=8080)

    args = parser.parse_args()

    ip = args.address
    port = args.port

    if not 0 < port < 65536:
        print("Error: port out of range (1 ~ 65535).")
        return

    try:
        listener = Listener(ip)
        await listener.start_server(port)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print("Error: port is already in use.")
            return
        else:
            raise
    except ValueError:
        print("Error: invalid IP address.")
        return

    print(f"Started server on {ip}:{port}")
    async for client in listener.incoming():
        task = asyncio.create_task(handle_client(client))
        tasks.append(task)

    await asyncio.gather(*tasks)


asyncio.run(main())
