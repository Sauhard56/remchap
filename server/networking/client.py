import socket
import asyncio

from ipaddress import ip_address
from typing import Sequence


class Client:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        sock: socket.socket = writer.get_extra_info("socket")
        ip, port = sock.getpeername()[:2]

        self._write_lock = asyncio.Lock()
        self._reader = reader
        self._writer = writer
        self._connected = True
        self._ip = ip_address(ip)
        self._port = port

    async def read(self, n: int = -1) -> bytes:
        data_read = await self._reader.read(n)
        if not data_read:
            self._connected = False

        return data_read
    
    async def write(self, data: bytes | bytearray | Sequence[int]) -> None:
        if self._connected:
            async with self._write_lock:
                try:
                    self._writer.write(data)
                    await self._writer.drain()
                except ConnectionResetError:
                    self.close()


    def close(self) -> None:
        self._connected = False
        self._writer.close()

    @property
    def ip(self) -> str:
        return str(self._ip.ipv4_mapped or self._ip)
    
    @property
    def port(self) -> int:
        return self._port
    
    @property
    def connected(self) -> bool:
        return self._connected
