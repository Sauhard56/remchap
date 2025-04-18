import asyncio
import socket

from ipaddress import ip_address
from typing import AsyncGenerator

from .client import Client

class Listener:
    def __init__(self, ip: str) -> None:
        self._port = None
        self._running = False
        self._ip = ip_address(ip)
        self._server: asyncio.Server = None
        self._connection_queue: asyncio.Queue[Client] = asyncio.Queue()

    async def start_server(self, port: int) -> None:
        if self._running:
            raise RuntimeError("listener already running on port", self._port)

        family = socket.AF_INET if self._ip.version == 4 else socket.AF_INET6
        sock = socket.socket(family, socket.SOCK_STREAM, socket.IPPROTO_TCP)

        if family == socket.AF_INET6:
            sock.setsockopt(socket.IPPROTO_IPV6,
                            socket.IPV6_V6ONLY, 0) # Allow both IPv4 and IPv6 connections

        sock.bind((str(self._ip), port))
        sock.setblocking(False)

        self._server = await asyncio.start_server(self._handle_client, sock=sock)
        self._port = port
        self._running = True

    def stop_server(self) -> None:
        if self._running:
            self._server.close()
            self._server.close_clients()

            self._server = None
            self._port = None
            self._running = False

            self._connection_queue.shutdown(True)
            self._connection_queue = asyncio.Queue()

    async def incoming(self) -> AsyncGenerator[Client]:
        while self._running:
            try:
                yield await self._connection_queue.get()
            except (asyncio.QueueShutDown, asyncio.CancelledError):
                return

    @property
    def port(self) -> int | None:
        return self._port

    @property
    def ip(self) -> str:
        return str(self._ip)

    @property
    def running(self) -> bool:
        return self._running

    async def _handle_client(self, reader: asyncio.StreamReader,
                             writer: asyncio.StreamWriter) -> None:
        client = Client(reader, writer)
        await self._connection_queue.put(client)
