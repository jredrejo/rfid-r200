"""Custom exceptions for R200 RFID library."""


class R200Error(Exception):
    """Base exception for R200 library."""

    pass


class R200CommunicationError(R200Error):
    """Raised when communication with R200 module fails."""

    pass


class R200ParseError(R200Error):
    """Raised when parsing R200 response fails."""

    pass


class R200TimeoutError(R200Error):
    """Raised when communication with R200 module times out."""

    pass


class R200CommandError(R200Error):
    """Raised when R200 module rejects a command."""

    pass
