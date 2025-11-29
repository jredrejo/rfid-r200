# Contributing to rfid-r200

Thank you for your interest in contributing to the rfid-r200 library! This document provides guidelines and information for contributors.

## ToDo
Current library implements only the R200 protocol commands that I needed for my projects: mainly read tags and some power adjustements in the receiver.
None of the tags write commands is implemented.


## Getting Started

### Prerequisites

- Python 3.12 or higher
- `uv` package manager (recommended) or `pip`
- R200 RFID module for testing
- Serial port access permissions

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jredrejo/rfid-r200.git
   cd rfid-r200
   ```

2. Install dependencies and set up development environment:
   ```bash
   uv pip install -e .[dev,test]
   uv sync --group dev
   ```

3. Install pre-commit hooks:
   ```bash
   uv tool install pre-commit --with pre-commit-uv
   pre-commit install
   ```

4. Run tests to verify setup:
   ```bash
   make test
   ```

## Development Workflow

### Code Style

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **mypy**: Type checking
- **flake8**: Linting
- **pytest**: Testing

Before submitting a pull request, ensure all checks pass using the Makefile:

```bash
# Run all quality checks (format, type-check, lint, test)
make check

# Or run individual checks:
make format    # Format code with black
make type-check # Type check with mypy
make lint      # Lint with flake8
make test      # Run tests with pytest

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Making Changes

1. Create a new branch for your feature/bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the existing code patterns and conventions.

3. Add tests for new functionality or bug fixes.

4. Ensure all tests pass and code quality checks are satisfied.

5. Commit your changes with clear, descriptive messages:
   ```bash
   git commit -m "Add new feature: description of changes"
   ```

6. Push to your fork and create a pull request.

### Testing

#### Running Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_sync_reader.py
```

#### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test function names
- Test both success and error cases
- Mock external dependencies when appropriate
- Follow pytest conventions

Example test structure:
```python
import pytest
from unittest.mock import Mock, patch
from rfid_r200 import R200

class TestR200:
    def test_init(self):
        """Test R200 initialization."""
        with patch('serial.Serial') as mock_serial:
            mock_port = Mock()
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0", 115200, debug=False)
            assert rfid.port_name == "/dev/ttyUSB0"
            assert rfid.speed == 115200
            assert rfid.debug is False

    def test_read_tags_success(self):
        """Test successful tag reading."""
        with patch('serial.Serial') as mock_serial:
            mock_port = Mock()
            # Mock response with proper side_effect for read() loop
            mock_port.read.side_effect = [
                bytes([0xAA, 0x01, 0x27, 0x00, 0x00, 0xB8, 0xDD]),
                b""  # Empty bytes to end the read loop
            ]
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            tags, errors = rfid.read_tags()
            assert isinstance(tags, list)

    def test_read_tags_error(self):
        """Test tag reading error handling."""
        with patch('serial.Serial') as mock_serial:
            mock_port = Mock()
            mock_port.read.side_effect = IOError("Serial communication failed")
            mock_serial.return_value = mock_port

            rfid = R200("/dev/ttyUSB0")
            with pytest.raises(IOError):
                rfid.send_command(0x27)
```

## Project Structure

```
src/rfid_r200/
├── __init__.py                 # Package exports
├── exceptions.py               # Custom exceptions
├── constants.py                # Protocol constants
├── utils.py                    # Shared utilities and data classes
├── rfid_reader_sync.py         # Synchronous R200 implementation
├── rfid_reader_async.py        # Asynchronous R200 implementation

src/
├── main.py                     # Sync usage example
└── main_async.py               # Async usage example

tests/                          # Test suite with fixtures
docs/                           # Documentation and datasheets
```

## Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Write descriptive docstrings
- Keep functions and methods focused on a single responsibility
- Use meaningful variable and function names

### Documentation

- Update relevant sections in README.md for user-facing changes
- Add docstrings to new functions and classes
- Update CHANGELOG.md for significant changes
- Ensure documentation stays in sync with code changes

### Git Commit Messages

Use clear, descriptive commit messages:

- Use present tense ("Add feature" not "Added feature")
- Capitalize the subject line
- Don't end subject line with a period
- Separate subject from body with blank line
- Explain what and why, not how

Examples:
```
Add support for custom demodulator parameters

Implements new methods to configure receiver demodulator
parameters including mixer gain, IF gain, and threshold
settings. This allows fine-tuning for different tag types
and environments.

Fix serial port timeout handling

Previous implementation could hang indefinitely when
device doesn't respond. Added proper timeout handling
with R200TimeoutError exception.
```

## Submitting Changes

### Pull Request Process

1. Ensure your branch is up to date with main:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. Create a pull request with:
   - Clear title and description
   - Reference any relevant issues
   - Include screenshots if applicable
   - Describe testing performed

3. Wait for code review and address any feedback.

### Review Process

- All changes require code review approval
- Automated tests must pass
- Code quality checks must pass
- Documentation may be updated as needed

## Getting Help

- Check existing [Issues](https://github.com/jredrejo/rfid-r200/issues)
- Create a new issue for bugs or feature requests

## License

By contributing to this project, you agree that your contributions will be licensed under the GNU General Public License v3.0.
