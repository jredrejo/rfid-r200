"""Tests for synchronous R200 reader."""

from unittest.mock import Mock
from unittest.mock import patch

import pytest
from rfid_r200 import R200


class TestR200:
    """Test cases for the R200 synchronous reader."""

    def test_init_basic(self):
        """Test basic R200 initialization."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0", 115200, debug=False)

            assert rfid.port_name == "/dev/ttyUSB0"
            assert rfid.speed == 115200
            assert rfid.debug is False
            mock_serial.assert_called_once_with(
                port="/dev/ttyUSB0",
                baudrate=115200,
                parity="N",
                stopbits=1,
                bytesize=8,
                timeout=1.0,
                write_timeout=1.0,
            )

    def test_init_with_debug(self):
        """Test R200 initialization with debug enabled."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0", 9600, debug=True)

            assert rfid.debug is True
            mock_serial.assert_called_once_with(
                port="/dev/ttyUSB0",
                baudrate=9600,
                parity="N",
                stopbits=1,
                bytesize=8,
                timeout=1.0,
                write_timeout=1.0,
            )

    def test_init_custom_timeout(self):
        """Test R200 initialization with custom timeout."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            mock_serial.return_value = mock_port

            R200("/dev/ttyUSB0", 115200, timeout=2.5)

            mock_serial.assert_called_once_with(
                port="/dev/ttyUSB0",
                baudrate=115200,
                parity="N",
                stopbits=1,
                bytesize=8,
                timeout=2.5,
                write_timeout=2.5,
            )

    def test_close(self):
        """Test closing the R200 connection."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            rfid.close()

            mock_port.close.assert_called_once()

    def test_context_manager(self):
        """Test using R200 as a context manager."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            mock_serial.return_value = mock_port

            with R200("/dev/ttyUSB0") as rfid:
                assert rfid is not None

            mock_port.close.assert_called_once()

    def test_send_command_basic(self):
        """Test sending a basic command."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            rfid.send_command(0x03)  # CMD_GET_MODULE_INFO

            # Verify that data was written to the serial port
            mock_port.write.assert_called()
            call_args = mock_port.write.call_args[0][0]
            assert isinstance(call_args, bytes)
            assert len(call_args) > 0

    def test_send_command_with_params(self):
        """Test sending a command with parameters."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            rfid.send_command(0xB6, [0x1E])  # CMD_SET_TRANSMIT_POWER with value

            mock_port.write.assert_called()
            call_args = mock_port.write.call_args[0][0]
            assert isinstance(call_args, bytes)
            assert len(call_args) > 0

    def test_receive_basic(self):
        """Test basic response receiving."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            # Mock a simple response - need to mock read() to return bytes first, then empty to stop loop
            mock_port.read.side_effect = [
                bytes([0xAA, 0x01, 0x03, 0x00, 0x00, 0xDD]),
                b"",
            ]
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            responses = rfid.receive()

            assert isinstance(responses, list)
            mock_port.read.assert_called()

    def test_read_tags_no_tags(self):
        """Test reading tags when no tags are present."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            # Mock empty response indicating no tags - checksum needs to be valid
            mock_port.read.side_effect = [
                bytes([0xAA, 0x01, 0x27, 0x00, 0x00, 0xB8, 0xDD]),
                b"",
            ]
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            tags, errors = rfid.read_tags()

            assert isinstance(tags, list)

    def test_read_tags_with_tags(self):
        """Test reading tags when tags are present."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            # Mock a response with tag data
            mock_port.read.side_effect = [
                bytes(
                    [
                        0xAA,
                        0x02,
                        0x27,
                        0x00,
                        0x12,  # Header with 18 bytes of data
                        0xE2,
                        0x80,  # RSSI and PC
                        0x01,
                        0x23,
                        0x45,
                        0x67,
                        0x89,
                        0xAB,
                        0xCD,
                        0xEF,  # EPC (8 bytes)
                        0x12,
                        0x34,
                        0x56,
                        0x78,
                        0x9A,
                        0xBC,
                        0xDE,
                        0xF0,  # More EPC data
                        0x12,
                        0x34,  # CRC
                        0x43,
                        0x21,  # Checksum
                        0xDD,  # Frame end
                    ]
                ),
                b"",
            ]
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            tags, errors = rfid.read_tags()

            assert isinstance(tags, list)

    def test_hw_info(self):
        """Test getting hardware information."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            # Mock module info response
            mock_port.read.side_effect = [
                bytes(
                    [
                        0xAA,
                        0x01,
                        0x03,
                        0x00,
                        0x08,  # Header with 8 bytes of data
                        0x52,
                        0x32,
                        0x30,
                        0x30,  # "R200"
                        0x01,
                        0x02,
                        0x03,
                        0x04,  # Version/info
                        0x0A,
                        0x00,  # Checksum
                        0xDD,  # Frame end
                    ]
                ),
                b"",
            ]
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            info = rfid.hw_info()

            assert info is not None
            mock_port.write.assert_called()  # Command was sent

    def test_set_power(self):
        """Test setting transmit power."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            # Mock power set response
            mock_port.read.side_effect = [
                bytes(
                    [
                        0xAA,
                        0x01,
                        0xB6,
                        0x00,
                        0x01,  # Header with 1 byte of data
                        0x00,  # Success code
                        0x5B,
                        0x00,  # Checksum
                        0xDD,  # Frame end
                    ]
                ),
                b"",
            ]
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            result = rfid.set_power(26)

            assert result is not None
            mock_port.write.assert_called()

    def test_get_power(self):
        """Test getting transmit power."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            # Mock power response
            mock_port.read.side_effect = [
                bytes(
                    [
                        0xAA,
                        0x01,
                        0xB7,
                        0x00,
                        0x01,  # Header with 1 byte of data
                        0x1A,  # Power value 26 dBm
                        0x6C,
                        0x00,  # Checksum
                        0xDD,  # Frame end
                    ]
                ),
                b"",
            ]
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            power = rfid.get_power()

            assert power is not None
            mock_port.write.assert_called()

    def test_invalid_port(self):
        """Test handling of invalid serial port."""
        with patch("serial.Serial", side_effect=OSError("No such device")):
            with pytest.raises(OSError) as exc_info:
                R200("/dev/ttyUSB99")
            assert "Failed to open serial port" in str(exc_info.value)

    def test_serial_communication_error(self):
        """Test handling of serial communication errors."""
        with patch("serial.Serial") as mock_serial:
            mock_port = Mock()
            mock_port.write.side_effect = IOError("Communication error")
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")

            with pytest.raises(IOError):
                rfid.send_command(0x03)
