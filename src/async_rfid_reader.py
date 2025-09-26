import asyncio
import binascii
from typing import cast
from typing import List

import serial_asyncio

from .constants import CMD_GET_MODULE_INFO
from .constants import CMD_MULTIPLE_POLL_INSTRUCTION
from .utils import R200AsyncInterface
from .utils import R200PoolResponse
from .utils import R200Response


class R200Async(R200AsyncInterface):
    def __init__(
        self,
        port: str,
        speed: int = 115200,
        debug: bool = False,
        idle_timeout: float = 0.15,
        read_chunk: int = 512,
    ) -> "R200Async":
        """
        Open the serial connection asynchronously.

        idle_timeout: max gap (s) to consider we've received all frames for a request
        read_chunk:   bytes per read from the serial stream
        """
        self.debug = debug
        self.port = port
        self.speed = speed
        self.reader = None
        self.writer = None
        self.transport = None
        self.read_chunk = read_chunk
        self.idle_timeout = idle_timeout

    async def connect(self):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.port, baudrate=self.speed
        )
        self.transport = cast(serial_asyncio.SerialTransport, self.writer.transport)

    async def close(self) -> None:
        if self.reader:
            self.transport.close()
            await asyncio.sleep(0.1)
        else:
            raise RuntimeError("Serial port not opened")

    async def send_command(self, command: int, parameters: List[int] = None) -> None:

        out = self._send_command(command, parameters)
        self.transport.write(bytes(out))
        await asyncio.sleep(0.05)  # Ensure bytes are sent

    async def _read_all_available(self) -> bytes:
        """
        Read until no more bytes arrive for idle_timeout seconds.
        """
        buf = bytearray()
        while True:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(self.read_chunk), timeout=self.idle_timeout
                )
            except asyncio.TimeoutError:
                break  # idle window passed; stop reading
            if not chunk:
                break
            buf.extend(chunk)
            # Continue loop to collect more until idle gap hits
        if self.debug and buf:
            print(f"[RX] {binascii.hexlify(buf).decode()}")
        return bytes(buf)

    async def receive(self) -> List[R200Response]:
        buffer = bytearray(await self._read_all_available())
        responses = self._parse_buffer(buffer)

        return responses

    async def read_tags(self) -> List[R200PoolResponse]:
        await self.send_command(CMD_MULTIPLE_POLL_INSTRUCTION, [0x22, 0x00, 0x0A])
        responses = await self.receive()

        return self._read_tags(responses)

    async def hw_info(self) -> List[R200PoolResponse]:
        await self.send_command(
            CMD_GET_MODULE_INFO,
            [
                0x00,
            ],
        )
        responses = await self.receive()
        for resp in responses:
            if resp.command == CMD_GET_MODULE_INFO:
                return "".join(map(chr, resp.params[1:]))
        return Exception("Error reading RFID")
