import asyncio
import binascii
from typing import cast
from typing import List

import serial_asyncio

from .constants import CMD_ACQUIRE_TRANSMIT_POWER
from .constants import CMD_GET_MODULE_INFO
from .constants import CMD_GET_RECEIVER_DEMODULATOR_PARAMETERS
from .constants import CMD_MULTIPLE_POLL_INSTRUCTION
from .constants import CMD_SET_RECEIVER_DEMODULATOR_PARAMETERS
from .constants import CMD_SET_TRANSMIT_POWER
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
                return bytearray(resp.params).decode()
        return Exception("Error reading RFID")

    async def get_power(self) -> float:
        """Get reader power"""
        """ Returns a float with the dBm value """
        await self.send_command(CMD_ACQUIRE_TRANSMIT_POWER)
        responses = await self.receive()
        for resp in responses:
            if resp.command == CMD_ACQUIRE_TRANSMIT_POWER:
                return int.from_bytes(bytes(resp.params), "big") / 100.0
        raise Exception("Error reading RFID")

    async def set_power(self, power: float) -> bool:
        """Set reader power"""
        """ power is a float with the dBm value """
        # Beware: tested modules only support values from 15 to 26 dBm
        value = int(power * 100)
        params = list(value.to_bytes(2, "big"))
        await self.send_command(CMD_SET_TRANSMIT_POWER, params)
        responses = await self.receive()
        for resp in responses:
            if resp.command == CMD_SET_TRANSMIT_POWER:
                return resp.params == [0]
        raise Exception("Error setting power")

    async def get_demodulator_params(self) -> dict[str, int]:
        """Get demodulator parameters"""
        """ Returns a dict with the parameters """
        """
        Sent: aa00f10000f1dd
        [RX] aa01f10004020600b0aedd
        Buffer: aa01f10004020600b0aedd
        Demodulator parameters: {'Mixer_ G': 2, 'IF_ G': 6, 'Signal demodulation threshold Thrd:': 176}
        """
        await self.send_command(CMD_GET_RECEIVER_DEMODULATOR_PARAMETERS)
        responses = await self.receive()
        for resp in responses:
            if resp.command == CMD_GET_RECEIVER_DEMODULATOR_PARAMETERS:
                return {
                    "Mixer_ G": resp.params[0],
                    "IF_ G": resp.params[1],
                    "Thrd:": int.from_bytes(bytes(resp.params[2:]), "big"),
                }
        raise Exception("Error reading RFID")

    async def set_demodulator_params(self, mixer_g: int, if_g: int, thrd: int) -> bool:
        """Set demodulator parameters"""
        """ Returns a bool """
        """
        set_demodulator_params(mixer_g=2, if_g=7, thrd=100)
        Sent: aa00f000040207006461dd
        Buffer: aa01f0000100f2dd
        """
        params = [mixer_g, if_g] + list(thrd.to_bytes(2, "big"))
        await self.send_command(CMD_SET_RECEIVER_DEMODULATOR_PARAMETERS, params)
        responses = await self.receive()
        for resp in responses:
            if resp.command == CMD_SET_RECEIVER_DEMODULATOR_PARAMETERS:
                return resp.params == [0]
        raise Exception("Error setting demodulator parameters")
