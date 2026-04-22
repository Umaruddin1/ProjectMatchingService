"""Custom exceptions."""


class ProcessingException(Exception):
    """Base exception for processing errors."""
    pass


class FileValidationException(ProcessingException):
    """Raised when file validation fails."""
    pass


class ParsingException(ProcessingException):
    """Raised when parsing fails."""
    pass


class ValidationException(ProcessingException):
    """Raised when data validation fails."""
    pass


class MatchingException(ProcessingException):
    """Raised when matching logic fails."""
    pass


class ExportException(ProcessingException):
    """Raised when export fails."""
    pass
