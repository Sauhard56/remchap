import asyncio
import socket

from typing import Sequence


class Client:
    def __init__(self) -> None:
        self._write_lock = asyncio.Lock()
        self._connected = False
        self._reader = None
        self._writer = None
        self._port = None
        self._ip = None

    async def connect(self, host: str, port: int, timeout: int | None = None) -> None:
        if self._connected:
            self.disconnect()

        self._reader, self._writer = await asyncio.wait_for(
            await asyncio.open_connection(host, port), timeout)

        sock: socket.socket = self._writer.get_extra_info("socket")
        self._ip, self._port = sock.getpeername()[:2]
        self._connected = True

    async def read(self, n: int = -1) -> bytes:
        data_read = await self._reader.read(n)
        if not data_read:
            self.disconnect()

        return data_read

    async def write(self, data: bytes | bytearray | Sequence[int]) -> None:
        if self._connected:
            async with self._write_lock:
                try:
                    self._writer.write(data)
                    await self._writer.drain()
                except ConnectionResetError:
                    self.disconnect()

    def disconnect(self) -> None:
        if self._connected:
            self._ip = None
            self._port = None

            self._writer.close()
            self._writer = None
            self._reader = None

            self._connected = False

    @property
    def ip(self) -> str | None:
        return self._ip

    @property
    def port(self) -> int | None:
        return self._port

    @property
    def connected(self) -> bool:
        return self._connected
