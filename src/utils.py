import binascii
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Tuple

from .constants import CMD_EXECUTION_FAILURE
from .constants import CMD_SINGLE_POLL_INSTRUCTION
from .constants import ERR_COMMAND_ERROR
from .constants import ERR_INVENTORY_FAIL
from .constants import ERR_READ_FAIL
from .constants import FRAME_TYPE_COMMAND
from .constants import FRAME_TYPE_NOTIFICATION
from .constants import FRAME_TYPE_RESPONSE
from .constants import R200_COMMAND_POS
from .constants import R200_FRAME_END
from .constants import R200_FRAME_HEADER
from .constants import R200_HEADER_POS
from .constants import R200_PARAM_LENGTH_LSB_POS
from .constants import R200_PARAM_LENGTH_MSB_POS
from .constants import R200_PARAM_POS
from .constants import R200_TYPE_POS


@dataclass
class R200Response:
    type: int
    command: int
    checksum: int
    checksum_ok: bool
    params: List[int]


@dataclass
class R200PoolResponse:
    rssi: int = 0
    pc: int = 0
    epc: List[int] = None
    crc: int = 0

    def __post_init__(self):
        if self.epc is None:
            self.epc = []

    def parse(self, params: List[int]) -> None:
        if len(params) < 17:
            raise ValueError("Not enough data")
        self.rssi = params[0]
        self.pc = (params[1] << 8) + params[2]
        self.epc = params[3:15]
        self.crc = (params[15] << 8) + params[16]


class R200ErrorResponse:
    def __init__(self, error: List[int]):
        self.error = error
        self.message = ""

    def parse(self) -> str:
        if not self.error:
            self.message = "Unknown error"
        elif self.error[0] == ERR_INVENTORY_FAIL:
            self.message = "No tags detected"
        elif self.error[0] == ERR_COMMAND_ERROR:
            self.message = "Can't execute command"
        elif self.error[0] == ERR_READ_FAIL:
            self.message = "Read failed"
        else:
            self.message = f"Error: 0x{self.error[0]:02x}"
        return self.message


class CommonR200Interface:
    @staticmethod
    def _checksum(payload: List[int], param_len: int) -> int:
        """Sum of bytes from Type through last parameter (uint8 wrap)."""
        checksum_region = bytes(payload[R200_TYPE_POS : R200_PARAM_POS + param_len])
        return sum(checksum_region) & 0xFF

    def _send_command(self, command: int, parameters: List[int] = None) -> List[int]:
        """
        Send command to R200 module

        Args:
            command: Command code
            parameters: List of parameter bytes (optional)
        """
        if parameters is None:
            parameters = []

        out = []

        out.append(R200_FRAME_HEADER)
        out.append(FRAME_TYPE_COMMAND)
        out.append(command)

        # Parameter length (MSB, LSB)
        param_len = len(parameters)
        out.append((param_len >> 8) & 0xFF)
        out.append(param_len & 0xFF)

        if parameters:
            out.extend(parameters)

        out.append(self._checksum(out, param_len))
        out.append(R200_FRAME_END)
        if self.debug:
            print(f"Sent: {binascii.hexlify(bytes(out)).decode()}")

        return out

    def _parse_buffer(self, buffer: bytes) -> List[R200Response]:
        """
        Receive buffer from R200 module

        Returns:
            List of R200Response objects
        """
        responses = []
        # Parse all responses in buffer
        while len(buffer) > 0:
            if self.debug:
                print(f"Buffer: {binascii.hexlify(buffer).decode()}")

            # Minimum packet size (header+type+cmd+len(2)+checksum+end) = 7
            if len(buffer) < 7:
                break

            if buffer[R200_HEADER_POS] == R200_FRAME_HEADER:
                # Check frame type
                if buffer[R200_TYPE_POS] in [
                    FRAME_TYPE_RESPONSE,
                    FRAME_TYPE_NOTIFICATION,
                ]:
                    resp = R200Response(
                        type=buffer[R200_TYPE_POS],
                        command=buffer[R200_COMMAND_POS],
                        checksum=0,
                        checksum_ok=False,
                        params=[],
                    )

                    param_len = (buffer[R200_PARAM_LENGTH_MSB_POS] << 8) + buffer[
                        R200_PARAM_LENGTH_LSB_POS
                    ]

                    # Check if we have enough data
                    if len(buffer) < R200_PARAM_POS + param_len + 2:
                        break

                    resp.params = list(
                        buffer[R200_PARAM_POS : R200_PARAM_POS + param_len]
                    )

                    checksum = self._checksum(buffer, param_len)
                    if checksum == buffer[R200_PARAM_POS + param_len]:
                        resp.checksum_ok = True
                        resp.checksum = checksum

                    responses.append(resp)

                    # Remove processed packet from buffer
                    buffer = buffer[R200_PARAM_POS + param_len + 2 :]
                else:
                    # Invalid frame type, skip this byte
                    buffer = buffer[1:]
            else:
                # Invalid header, skip this byte
                buffer = buffer[1:]

        return responses

    def _read_tags(
        self, responses: List[R200Response]
    ) -> Tuple[List[R200PoolResponse], Optional[Exception]]:
        """
        Read RFID tags using multiple poll instruction

        Returns:
            List of R200PoolResponse objects containing tag data
            Optional exception if an error occurs
        """
        pool: List[R200PoolResponse] = []
        epc_ids: set[str] = set()
        err: Optional[Exception] = None

        for resp in responses:
            if resp.command == CMD_SINGLE_POLL_INSTRUCTION:
                item = R200PoolResponse()
                try:
                    item.parse(resp.params)

                    # Convert EPC to hex string for comparison
                    epc_hex = binascii.hexlify(bytes(item.epc)).decode()

                    if epc_hex not in epc_ids:
                        epc_ids.add(epc_hex)
                        pool.append(item)

                except ValueError as e:
                    raise RuntimeError(f"Error parsing tag data: {e}")

            elif resp.command == CMD_EXECUTION_FAILURE:
                error_data = R200ErrorResponse(resp.params)
                error_msg = error_data.parse()
                err = RuntimeError(f"Error reading RFID: {error_msg}")
            else:
                # Sets a generic undefined error for other commands
                err = RuntimeError("Undefined error")

        return pool, err


class R200AsyncInterface(ABC, CommonR200Interface):
    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def send_command(self, command: int, parameters: List[int]) -> None:
        pass

    @abstractmethod
    async def receive(self) -> List[R200Response]:
        pass

    @abstractmethod
    async def read_tags(self) -> List[R200PoolResponse]:
        pass

    @abstractmethod
    def _read_all_available(self) -> bytes:
        pass


class R200Interface(ABC, CommonR200Interface):
    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def send_command(self, command: int, parameters: List[int]) -> None:
        pass

    @abstractmethod
    def receive(self) -> List[R200Response]:
        pass

    @abstractmethod
    def read_tags(self) -> List[R200PoolResponse]:
        pass

    @abstractmethod
    def _read_all_available(self) -> bytes:
        pass
