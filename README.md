# R200 RFID Module Python Library

A Python library for interfacing with R200 RFID modules via serial communication.

## Features

- **Partial R200 Protocol Support**: Implements the parts of the R200 RFID module communication protocol
- **Object-Oriented Design**: Clean, maintainable code with abstract interfaces
- **Type Safety**: Full type hints for better IDE support and code reliability
- **Error Handling**: Comprehensive error handling with descriptive messages
- **Debug Support**: Optional debug output for troubleshooting
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Sync and Async**: Supports both synchronous and asynchronous interfaces

## Installation

### Install from PyPI

```bash
pip install rfid-r200
```

### Development Installation

```bash
git clone https://github.com/jredrejo/rfid-r200.git
cd rfid-r200
uv pip install -e .[dev,test]
uv sync --group dev
```

### Quick Start Examples

```bash
# Run synchronous example
uv run src/main.py

# Run asynchronous example
uv run src/main_async.py
```

## Quick Start

### Synchronous Example

```python
from rfid_r200 import R200
import binascii

# Initialize the RFID module
rfid = R200("/dev/ttyUSB0", 115200, debug=True)  # Linux
# rfid = R200("COM3", 115200, debug=True)  # Windows

try:
    # Read RFID tags
    tags, errors = rfid.read_tags()

    print(f"Found {len(tags)} tags:")
    for i, tag in enumerate(tags):
        epc_hex = binascii.hexlify(bytes(tag.epc)).decode()
        print(f"Tag {i+1}: EPC={epc_hex}, RSSI={tag.rssi}")

finally:
    rfid.close()
```

### Asynchronous Example

```python
from rfid_r200 import AsyncR200
import binascii
import asyncio

async def main():
    # Initialize the RFID module
    rfid = AsyncR200("/dev/ttyUSB0", 115200, debug=True)

    try:
        # Read RFID tags
        tags, errors = await rfid.read_tags()

        print(f"Found {len(tags)} tags:")
        for i, tag in enumerate(tags):
            epc_hex = binascii.hexlify(bytes(tag.epc)).decode()
            print(f"Tag {i+1}: EPC={epc_hex}, RSSI={tag.rssi}")
    finally:
        await rfid.close()

asyncio.run(main())
```

### Using as Context Manager

```python
from rfid_r200 import R200

# Automatically closes the port when exiting the block
with R200("/dev/ttyUSB0") as rfid:
    tags, errors = rfid.read_tags()
    for tag in tags:
        print(f"Found tag: {tag.epc}")
```

## API Reference

### Synchronous Interface (R200)

```python
from rfid_r200 import R200
```

### Asynchronous Interface (AsyncR200)

```python
from rfid_r200 import AsyncR200
```

### R200 / AsyncR200 Constructor

```python
R200(port: str, speed: int = 115200, debug: bool = False, timeout: float = 1.0)
```

- `port`: Serial port name (e.g., "/dev/ttyUSB0", "COM3")
- `speed`: Baud rate (default: 115200)
- `debug`: Enable debug output (default: False)
- `timeout`: Serial port timeout in seconds (default: 1.0)

#### Methods

##### `read_tags() -> List[R200PoolResponse]`

Read all RFID tags in range. Returns a list of `R200PoolResponse` objects.

```python
tags = rfid.read_tags()
for tag in tags:
    print(f"EPC: {binascii.hexlify(bytes(tag.epc)).decode()}")
    print(f"RSSI: {tag.rssi}")
```

##### `send_command(command: int, parameters: List[int] = None) -> None`

Send a raw command to the R200 module.

```python
# Get module info
rfid.send_command(CMD_GET_MODULE_INFO)
responses = rfid.receive()
```

##### `receive() -> List[R200Response]`

Receive responses from the R200 module.

##### `close() -> None`

Close the serial port connection.

### Data Structures

#### R200PoolResponse

Contains RFID tag information:

- `rssi: int` - Signal strength
- `pc: int` - Protocol Control word
- `epc: List[int]` - Electronic Product Code
- `crc: int` - Cyclic Redundancy Check

#### R200Response

Raw response from the module:

- `type: int` - Frame type
- `command: int` - Command code
- `checksum: int` - Checksum value
- `checksum_ok: bool` - Checksum validation result
- `params: List[int]` - Response parameters

## Available Commands

The library includes constants for all R200 commands:

- `CMD_GET_MODULE_INFO` - Get module information
- `CMD_SINGLE_POLL_INSTRUCTION` - Single tag poll
- `CMD_MULTIPLE_POLL_INSTRUCTION` - Multiple tag poll
- `CMD_READ_LABEL` - Read tag data
- `CMD_WRITE_LABEL` - Write tag data
- `CMD_LOCK_LABEL` - Lock tag
- `CMD_KILL_TAG` - Kill tag
- And many more...

## Error Handling

The library provides comprehensive error handling:

```python
try:
    tags = rfid.read_tags()
except RuntimeError as e:
    print(f"RFID Error: {e}")
except ValueError as e:
    print(f"Data Error: {e}")
```

Common error messages:

- "No tags detected" - No RFID tags in range
- "Can't execute command" - Invalid command or parameters
- "Read failed" - Tag read operation failed

## Advanced Usage

### Custom Command Example

```python
# Send custom command with parameters
rfid.send_command(CMD_SET_TRANSMIT_POWER, [0x1E])  # Set power to 30dBm
responses = rfid.receive()

for resp in responses:
    if resp.checksum_ok:
        print(f"Command executed successfully")
    else:
        print(f"Checksum error")
```

### Working with Multiple Modules

```python
# Handle multiple RFID readers
readers = []
ports = ["/dev/ttyUSB0", "/dev/ttyUSB1"]

for port in ports:
    try:
        reader = R200(port, 115200)
        readers.append(reader)
    except Exception as e:
        print(f"Failed to initialize {port}: {e}")

# Read from all readers
all_tags = []
for reader in readers:
    try:
        tags = reader.read_tags()
        all_tags.extend(tags)
    except Exception as e:
        print(f"Error reading tags: {e}")

# Clean up
for reader in readers:
    reader.close()
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure your user has permission to access the serial port

   ```bash
   sudo usermod -a -G dialout $USER  # Linux
   ```

2. **Port Not Found**: Verify the correct port name

   ```bash
   ls /dev/tty*  # Linux
   ```

3. **No Response**: Check connections and baud rate settings

4. **Checksum Errors**: Enable debug mode to inspect raw communication

   ```python
   rfid = R200("/dev/ttyUSB0", debug=True)
   ```

### Debug Output

Enable debug mode to see raw serial communication:

```
Sent: aa00220003220a0add
Buffer: aa01220011001e9f12041e008bb2d1234567890123dd
```


## Development

### Setup Development Environment

```bash
# Install dependencies with uv
uv pip install -e .[dev,test]
uv sync --group dev

# Install pre-commit hooks
uv tool install pre-commit --with pre-commit-uv
pre-commit install
```

### Development Commands

```bash
# Run tests
make test

# Type checking
make type-check

# Code formatting
make format

# Linting
make lint

# All quality checks
make check

# Build package
make build

# Full development cycle
make dev
```

See `Makefile` for all available commands.

## License

GNU General Public License v3.0
