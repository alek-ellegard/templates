"""Exception classes for the CLI application."""

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes for the CLI application."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    USER_NOT_FOUND = 2
    USER_EXISTS = 3
    REPOSITORY_ERROR = 4
    VALIDATION_ERROR = 5


class CLIError(Exception):
    """Base exception for all CLI errors."""

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.GENERAL_ERROR) -> None:
        """Initialize CLI error.

        Args:
            message: Error message describing what went wrong
            exit_code: Exit code to return when this error occurs
        """
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code


class UserNotFoundError(CLIError):
    """Raised when a user cannot be found."""

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.USER_NOT_FOUND) -> None:
        """Initialize UserNotFoundError.

        Args:
            message: Error message describing which user was not found
            exit_code: Exit code (defaults to USER_NOT_FOUND)
        """
        super().__init__(message, exit_code)


class UserExistsError(CLIError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.USER_EXISTS) -> None:
        """Initialize UserExistsError.

        Args:
            message: Error message describing which user already exists
            exit_code: Exit code (defaults to USER_EXISTS)
        """
        super().__init__(message, exit_code)


class RepositoryError(CLIError):
    """Raised when repository operations fail."""

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.REPOSITORY_ERROR) -> None:
        """Initialize RepositoryError.

        Args:
            message: Error message describing what repository operation failed
            exit_code: Exit code (defaults to REPOSITORY_ERROR)
        """
        super().__init__(message, exit_code)


class ValidationError(CLIError):
    """Raised when data validation fails."""

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.VALIDATION_ERROR) -> None:
        """Initialize ValidationError.

        Args:
            message: Error message describing what validation failed
            exit_code: Exit code (defaults to VALIDATION_ERROR)
        """
        super().__init__(message, exit_code)
