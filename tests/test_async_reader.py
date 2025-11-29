"""Tests for asynchronous R200 reader."""

import asyncio
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from rfid_r200 import R200Async
from rfid_r200.utils import R200PoolResponse
from rfid_r200.utils import R200Response


class TestR200Async:
    """Test cases for R200Async asynchronous reader."""

    @pytest.mark.asyncio
    async def test_init_basic(self):
        """Test basic R200Async initialization."""
        rfid = R200Async("/dev/ttyUSB0", 115200, debug=False)

        assert rfid.port == "/dev/ttyUSB0"
        assert rfid.speed == 115200
        assert rfid.debug is False
        assert rfid.idle_timeout == 0.15
        assert rfid.read_chunk == 512

    @pytest.mark.asyncio
    async def test_init_with_options(self):
        """Test R200Async initialization with custom options."""
        rfid = R200Async(
            "/dev/ttyUSB0", 9600, debug=True, idle_timeout=0.2, read_chunk=1024
        )

        assert rfid.debug is True
        assert rfid.idle_timeout == 0.2
        assert rfid.read_chunk == 1024

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting to the RFID module."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()

            mock_conn.assert_called_once_with(url="/dev/ttyUSB0", baudrate=115200)

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing the connection."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            await rfid.close()

            mock_transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_command_basic(self):
        """Test sending a basic command."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            await rfid.send_command(0x03)  # CMD_GET_MODULE_INFO

            mock_transport.write.assert_called()
            call_args = mock_transport.write.call_args[0][0]
            assert isinstance(call_args, bytes)
            assert len(call_args) > 0

    @pytest.mark.asyncio
    async def test_send_command_with_params(self):
        """Test sending a command with parameters."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            await rfid.send_command(0xB6, [0x1E])  # CMD_SET_TRANSMIT_POWER

            mock_transport.write.assert_called()
            call_args = mock_transport.write.call_args[0][0]
            assert isinstance(call_args, bytes)
            assert len(call_args) > 0

    def _make_reader_mock(self, response_bytes: bytes) -> AsyncMock:
        """Helper to create a mock reader that returns data then times out."""
        mock_reader = AsyncMock()
        call_count = 0

        async def read_side_effect(n):
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                return response_bytes
            raise asyncio.TimeoutError()

        mock_reader.read.side_effect = read_side_effect
        return mock_reader

    @pytest.mark.asyncio
    async def test_receive_basic(self):
        """Test basic response receiving."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            response_bytes = bytes([0xAA, 0x01, 0x03, 0x00, 0x00, 0x43, 0xDD])
            mock_reader = self._make_reader_mock(response_bytes)
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            responses = await rfid.receive()

            assert isinstance(responses, list)
            assert len(responses) > 0
            assert isinstance(responses[0], R200Response)

    @pytest.mark.asyncio
    async def test_read_tags_no_tags(self):
        """Test reading tags when no tags are present."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            response_bytes = bytes([0xAA, 0x02, 0x27, 0x00, 0x01, 0x00, 0x49, 0xDD])
            mock_reader = self._make_reader_mock(response_bytes)
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            tags, errors = await rfid.read_tags()

            assert tags == []
            assert errors is not None

    @pytest.mark.asyncio
    async def test_read_tags_with_tags(self):
        """Test reading tags when tags are present."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            response_bytes = bytes(
                [
                    0xAA,
                    0x02,
                    0x22,
                    0x00,
                    0x11,
                    0xE2,
                    0x30,
                    0x00,
                    0x01,
                    0x23,
                    0x45,
                    0x67,
                    0x89,
                    0xAB,
                    0xCD,
                    0xEF,
                    0x12,
                    0x34,
                    0x56,
                    0x78,
                    0x12,
                    0x34,
                    0x48,
                    0xDD,
                ]
            )
            mock_reader = self._make_reader_mock(response_bytes)
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            tags, errors = await rfid.read_tags()

            assert len(tags) > 0
            assert isinstance(tags[0], R200PoolResponse)

    @pytest.mark.asyncio
    async def test_hw_info(self):
        """Test getting hardware information."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            response_bytes = bytes(
                [
                    0xAA,
                    0x01,
                    0x03,
                    0x00,
                    0x08,
                    0x52,
                    0x32,
                    0x30,
                    0x30,
                    0x01,
                    0x02,
                    0x03,
                    0x04,
                    0x0A,
                    0x00,
                    0xDD,
                ]
            )
            mock_reader = self._make_reader_mock(response_bytes)
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            info = await rfid.hw_info()

            assert info is not None
            mock_transport.write.assert_called()

    @pytest.mark.asyncio
    async def test_set_power(self):
        """Test setting transmit power."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            response_bytes = bytes([0xAA, 0x01, 0xB6, 0x00, 0x01, 0x00, 0x37, 0xDD])
            mock_reader = self._make_reader_mock(response_bytes)
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            result = await rfid.set_power(26)

            assert result is True
            mock_transport.write.assert_called()

    @pytest.mark.asyncio
    async def test_get_power(self):
        """Test getting transmit power."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            response_bytes = bytes(
                [0xAA, 0x01, 0xB7, 0x00, 0x02, 0x0A, 0x28, 0x71, 0xDD]
            )
            mock_reader = self._make_reader_mock(response_bytes)
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()
            power = await rfid.get_power()

            assert power == 26.0
            mock_transport.write.assert_called()

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling of connection errors."""
        with patch(
            "serial_asyncio.open_serial_connection",
            side_effect=OSError("Connection failed"),
        ):
            rfid = R200Async("/dev/ttyUSB0")

            with pytest.raises(OSError):
                await rfid.connect()

    @pytest.mark.asyncio
    async def test_serial_communication_error(self):
        """Test handling of serial communication errors."""
        with patch("serial_asyncio.open_serial_connection") as mock_conn:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_transport = Mock()
            mock_transport.write.side_effect = IOError("Communication error")
            mock_writer.transport = mock_transport
            mock_conn.return_value = (mock_reader, mock_writer)

            rfid = R200Async("/dev/ttyUSB0")
            await rfid.connect()

            with pytest.raises(IOError):
                await rfid.send_command(0x03)
