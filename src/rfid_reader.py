from typing import List
from typing import Optional
from typing import Tuple

import serial

from .constants import CMD_ACQUIRE_TRANSMIT_POWER
from .constants import CMD_GET_MODULE_INFO
from .constants import CMD_GET_RECEIVER_DEMODULATOR_PARAMETERS
from .constants import CMD_MULTIPLE_POLL_INSTRUCTION
from .constants import CMD_SET_RECEIVER_DEMODULATOR_PARAMETERS
from .constants import CMD_SET_TRANSMIT_POWER
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

    def hw_info(self) -> List[R200PoolResponse]:
        self.send_command(
            CMD_GET_MODULE_INFO,
            [
                0x00,
            ],
        )
        responses = self.receive()
        for resp in responses:
            if resp.command == CMD_GET_MODULE_INFO:
                return bytearray(resp.params).decode()
        return Exception("Error reading RFID")

    def get_power(self) -> float:
        """Get reader power"""
        """ Returns a float with the dBm value """
        self.send_command(CMD_ACQUIRE_TRANSMIT_POWER)
        responses = self.receive()
        for resp in responses:
            if resp.command == CMD_ACQUIRE_TRANSMIT_POWER:
                return int.from_bytes(bytes(resp.params), "big") / 100.0
        raise Exception("Error reading RFID")

    def set_power(self, power: float) -> bool:
        """Set reader power"""
        """ power is a float with the dBm value """
        # Beware: tested modules only support values from 15 to 26 dBm
        value = int(power * 100)
        params = list(value.to_bytes(2, "big"))
        self.send_command(CMD_SET_TRANSMIT_POWER, params)
        responses = self.receive()
        for resp in responses:
            if resp.command == CMD_SET_TRANSMIT_POWER:
                return resp.params == [0]
        raise Exception("Error setting power")

    def get_demodulator_params(self) -> dict[str, int]:
        """Get demodulator parameters"""
        """ Returns a dict with the parameters """
        """
        Sent: aa00f10000f1dd
        [RX] aa01f10004020600b0aedd
        Buffer: aa01f10004020600b0aedd
        Demodulator parameters: {'Mixer_ G': 2, 'IF_ G': 6, 'Signal demodulation threshold Thrd:': 176}
        """
        self.send_command(CMD_GET_RECEIVER_DEMODULATOR_PARAMETERS)
        responses = self.receive()
        for resp in responses:
            if resp.command == CMD_GET_RECEIVER_DEMODULATOR_PARAMETERS:
                return {
                    "Mixer_ G": resp.params[0],
                    "IF_ G": resp.params[1],
                    "Thrd:": int.from_bytes(bytes(resp.params[2:]), "big"),
                }
        raise Exception("Error reading RFID")

    def set_demodulator_params(self, mixer_g: int, if_g: int, thrd: int) -> bool:
        """Set demodulator parameters"""
        """ params is a dict with the parameters """
        """ Returns a bool """
        """
        Sent: aa00f004020600b0aedd
        [RX] aa01f004020600b0aedd
        Buffer: aa01f004020600b0aedd
        """
        params = [mixer_g, if_g] + list(thrd.to_bytes(2, "big"))
        self.send_command(CMD_SET_RECEIVER_DEMODULATOR_PARAMETERS, params)
        responses = self.receive()
        for resp in responses:
            if resp.command == CMD_SET_RECEIVER_DEMODULATOR_PARAMETERS:
                return resp.params == [0]
        raise Exception("Error setting demodulator parameters")
