# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-11-28

### Added
- PyPI packaging configuration
- Custom exception classes for better error handling
- Version management system
- Comprehensive package exports
- Tests


### Changed
- Renamed main reader files to follow Python naming conventions
- Updated import structure for package distribution
- Refactored project structure for PyPI compatibility

## [0.1.0] - 2024-09-28

### Added
- Initial implementation of R200 RFID module communication
- Synchronous interface via `rfid_reader.py`
- Asynchronous interface via `async_rfid_reader.py`
- Partial R200 protocol implementation
- Tag reading and management functionality
- Device configuration capabilities
- Cross-platform support (Linux, Windows, macOS)
- Comprehensive error handling
- Debug support for troubleshooting
- Type hints throughout codebase
- Example usage files

### Features
- Patial R200 Protocol Support
- Object-Oriented Design with abstract interfaces
- Tag Reading & Management with EPC, RSSI, CRC information
- Device Configuration (transmit power, demodulator parameters)
- Module information retrieval
- Cross-Platform Serial Communication
- Dual Interface Design (sync and async)
- Type Safety with full type hints
- Comprehensive Error Handling
- Debug Support
