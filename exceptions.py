"""Custom exceptions for the assistant chatbot."""


class AssistantError(Exception):
    """Base exception for assistant chatbot errors."""
    pass


class AuthenticationError(AssistantError):
    """Raised when authentication fails."""
    pass


class CalendarAPIError(AssistantError):
    """Raised when Google Calendar API operations fail."""
    pass


class ParsingError(AssistantError):
    """Raised when user input cannot be parsed."""
    pass


class ConfigurationError(AssistantError):
    """Raised when configuration is invalid."""
    pass
