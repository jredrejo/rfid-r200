"""RFID R200 Python Library

Pure Python library for interfacing with R200 RFID modules via serial communication.
"""

from .__version__ import __version__
from .constants import CMD_ACQUIRE_TRANSMIT_POWER
from .constants import CMD_GET_MODULE_INFO
from .constants import CMD_GET_RECEIVER_DEMODULATOR_PARAMETERS
from .constants import CMD_KILL_TAG
from .constants import CMD_LOCK_LABEL
from .constants import CMD_MULTIPLE_POLL_INSTRUCTION
from .constants import CMD_READ_LABEL
from .constants import CMD_SET_RECEIVER_DEMODULATOR_PARAMETERS
from .constants import CMD_SET_TRANSMIT_POWER
from .constants import CMD_SINGLE_POLL_INSTRUCTION
from .constants import CMD_STOP_MULTIPLE_POLL
from .constants import CMD_WRITE_LABEL
from .constants import ERR_ACCESS_FAIL
from .constants import ERR_COMMAND_ERROR
from .constants import ERR_FHSS_FAIL
from .constants import ERR_INVENTORY_FAIL
from .constants import ERR_KILL_FAIL
from .constants import ERR_LOCK_FAIL
from .constants import ERR_READ_FAIL
from .constants import ERR_WRITE_FAIL
from .constants import FRAME_TYPE_COMMAND
from .constants import FRAME_TYPE_NOTIFICATION
from .constants import FRAME_TYPE_RESPONSE
from .constants import R200_FRAME_END
from .constants import R200_FRAME_HEADER
from .exceptions import R200CommandError
from .exceptions import R200CommunicationError
from .exceptions import R200Error
from .exceptions import R200ParseError
from .exceptions import R200TimeoutError
from .rfid_reader_async import R200Async
from .rfid_reader_sync import R200
from .utils import R200PoolResponse
from .utils import R200Response

__all__ = [
    # Version
    "__version__",
    # Main classes
    "R200",
    "R200Async",
    # Data structures
    "R200PoolResponse",
    "R200Response",
    # Protocol constants
    "CMD_GET_MODULE_INFO",
    "CMD_SINGLE_POLL_INSTRUCTION",
    "CMD_MULTIPLE_POLL_INSTRUCTION",
    "CMD_STOP_MULTIPLE_POLL",
    "CMD_READ_LABEL",
    "CMD_WRITE_LABEL",
    "CMD_LOCK_LABEL",
    "CMD_KILL_TAG",
    "CMD_SET_TRANSMIT_POWER",
    "CMD_ACQUIRE_TRANSMIT_POWER",
    "CMD_SET_RECEIVER_DEMODULATOR_PARAMETERS",
    "CMD_GET_RECEIVER_DEMODULATOR_PARAMETERS",
    # Frame and protocol markers
    "R200_FRAME_HEADER",
    "R200_FRAME_END",
    "FRAME_TYPE_COMMAND",
    "FRAME_TYPE_RESPONSE",
    "FRAME_TYPE_NOTIFICATION",
    # Error codes
    "ERR_COMMAND_ERROR",
    "ERR_FHSS_FAIL",
    "ERR_INVENTORY_FAIL",
    "ERR_ACCESS_FAIL",
    "ERR_READ_FAIL",
    "ERR_WRITE_FAIL",
    "ERR_LOCK_FAIL",
    "ERR_KILL_FAIL",
    # Exceptions
    "R200Error",
    "R200CommunicationError",
    "R200ParseError",
    "R200TimeoutError",
    "R200CommandError",
]
