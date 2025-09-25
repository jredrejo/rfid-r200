from typing import List
from typing import Optional
from typing import Tuple

import serial

from .constants import CMD_MULTIPLE_POLL_INSTRUCTION
from .utils import R200Interface
from .utils import R200PoolResponse
from .utils import R200Response


class R200(R200Interface):
    """Python implementation of R200 RFID module library"""

    def __init__(
        self, port: str, speed: int = 115200, debug: bool = False, timeout: float = 1.0
    ):
        """
        Initialize R200 RFID module

        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3')
            speed: Baud rate (default: 115200)
            debug: Enable debug output (default: False)
        """
        self.debug = debug
        self.port = None

        try:
            self.port = serial.Serial(
                port=port,
                baudrate=speed,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=timeout,
                write_timeout=timeout,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to open serial port: {e}")

    def close(self) -> None:
        """Close the serial port connection"""
        if self.port and self.port.is_open:
            self.port.close()
        else:
            raise RuntimeError("Serial port not opened")

    def send_command(self, command: int, parameters: List[int] = None) -> None:
        """
        Send command to R200 module

        Args:
            command: Command code
            parameters: List of parameter bytes (optional)
        """
        out = self._send_command(command, parameters)

        self.port.write(bytes(out))

    def _read_all_available(self) -> bytes:
        """Read until no more bytes arrive within the configured timeout."""
        buf = bytearray()
        chunk = self.port.read(512)
        buf.extend(chunk)
        while chunk:
            chunk = self.port.read(512)
            buf.extend(chunk)
        return bytes(buf)

    def receive(self) -> List[R200Response]:
        """
        Receive responses from R200 module

        Returns:
            List of R200Response objects
        """
        buffer = bytearray(self._read_all_available())

        responses = self._parse_buffer(buffer)

        return responses

    def read_tags(self) -> Tuple[List[R200PoolResponse], Optional[Exception]]:
        """
        Read RFID tags using multiple poll instruction

        Returns:
            List of R200PoolResponse objects containing tag data
            Optional exception if an error occurs
        """
        self.send_command(CMD_MULTIPLE_POLL_INSTRUCTION, [0x22, 0x00, 0x0A])

        responses = self.receive()

        return self._read_tags(responses)
