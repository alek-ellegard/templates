"""Unit tests for exceptions module."""

import pytest

from mycli.exceptions import (
    CLIError,
    ExitCode,
    RepositoryError,
    UserExistsError,
    UserNotFoundError,
    ValidationError,
)


class TestExitCode:
    """Test ExitCode enum."""

    def test_exit_code_values(self) -> None:
        """Test that ExitCode has correct integer values."""
        assert ExitCode.SUCCESS == 0
        assert ExitCode.GENERAL_ERROR == 1
        assert ExitCode.USER_NOT_FOUND == 2
        assert ExitCode.USER_EXISTS == 3
        assert ExitCode.REPOSITORY_ERROR == 4
        assert ExitCode.VALIDATION_ERROR == 5

    def test_exit_code_is_int_enum(self) -> None:
        """Test that ExitCode values are integers."""
        assert isinstance(ExitCode.SUCCESS, int)
        assert isinstance(ExitCode.GENERAL_ERROR, int)


class TestCLIError:
    """Test CLIError base exception."""

    def test_cli_error_with_default_exit_code(self) -> None:
        """Test CLIError with default GENERAL_ERROR exit code."""
        error = CLIError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.exit_code == ExitCode.GENERAL_ERROR

    def test_cli_error_with_custom_exit_code(self) -> None:
        """Test CLIError with custom exit code."""
        error = CLIError("Custom error", exit_code=ExitCode.VALIDATION_ERROR)
        assert error.message == "Custom error"
        assert error.exit_code == ExitCode.VALIDATION_ERROR

    def test_cli_error_is_exception(self) -> None:
        """Test that CLIError is a proper exception."""
        error = CLIError("Test")
        assert isinstance(error, Exception)

    def test_cli_error_str_representation(self) -> None:
        """Test string representation of CLIError."""
        error = CLIError("Test message")
        assert str(error) == "Test message"


class TestUserNotFoundError:
    """Test UserNotFoundError exception."""

    def test_user_not_found_error_default_exit_code(self) -> None:
        """Test that UserNotFoundError has USER_NOT_FOUND exit code by default."""
        error = UserNotFoundError("User abc123 not found")
        assert error.message == "User abc123 not found"
        assert error.exit_code == ExitCode.USER_NOT_FOUND

    def test_user_not_found_error_inherits_from_cli_error(self) -> None:
        """Test that UserNotFoundError inherits from CLIError."""
        error = UserNotFoundError("User not found")
        assert isinstance(error, CLIError)

    def test_user_not_found_error_custom_exit_code(self) -> None:
        """Test that UserNotFoundError can override exit code."""
        error = UserNotFoundError("User not found", exit_code=ExitCode.GENERAL_ERROR)
        assert error.exit_code == ExitCode.GENERAL_ERROR


class TestUserExistsError:
    """Test UserExistsError exception."""

    def test_user_exists_error_default_exit_code(self) -> None:
        """Test that UserExistsError has USER_EXISTS exit code by default."""
        error = UserExistsError("User test@example.com already exists")
        assert error.message == "User test@example.com already exists"
        assert error.exit_code == ExitCode.USER_EXISTS

    def test_user_exists_error_inherits_from_cli_error(self) -> None:
        """Test that UserExistsError inherits from CLIError."""
        error = UserExistsError("User exists")
        assert isinstance(error, CLIError)

    def test_user_exists_error_custom_exit_code(self) -> None:
        """Test that UserExistsError can override exit code."""
        error = UserExistsError("User exists", exit_code=ExitCode.GENERAL_ERROR)
        assert error.exit_code == ExitCode.GENERAL_ERROR


class TestRepositoryError:
    """Test RepositoryError exception."""

    def test_repository_error_default_exit_code(self) -> None:
        """Test that RepositoryError has REPOSITORY_ERROR exit code by default."""
        error = RepositoryError("Failed to load users.json")
        assert error.message == "Failed to load users.json"
        assert error.exit_code == ExitCode.REPOSITORY_ERROR

    def test_repository_error_inherits_from_cli_error(self) -> None:
        """Test that RepositoryError inherits from CLIError."""
        error = RepositoryError("Repository error")
        assert isinstance(error, CLIError)

    def test_repository_error_custom_exit_code(self) -> None:
        """Test that RepositoryError can override exit code."""
        error = RepositoryError("Repo error", exit_code=ExitCode.GENERAL_ERROR)
        assert error.exit_code == ExitCode.GENERAL_ERROR


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_default_exit_code(self) -> None:
        """Test that ValidationError has VALIDATION_ERROR exit code by default."""
        error = ValidationError("Invalid email format")
        assert error.message == "Invalid email format"
        assert error.exit_code == ExitCode.VALIDATION_ERROR

    def test_validation_error_inherits_from_cli_error(self) -> None:
        """Test that ValidationError inherits from CLIError."""
        error = ValidationError("Validation failed")
        assert isinstance(error, CLIError)

    def test_validation_error_custom_exit_code(self) -> None:
        """Test that ValidationError can override exit code."""
        error = ValidationError("Validation error", exit_code=ExitCode.GENERAL_ERROR)
        assert error.exit_code == ExitCode.GENERAL_ERROR


class TestExceptionRaising:
    """Test that exceptions can be raised and caught properly."""

    def test_raise_and_catch_user_not_found_error(self) -> None:
        """Test raising and catching UserNotFoundError."""
        with pytest.raises(UserNotFoundError) as exc_info:
            raise UserNotFoundError("User xyz not found")
        assert exc_info.value.message == "User xyz not found"
        assert exc_info.value.exit_code == ExitCode.USER_NOT_FOUND

    def test_catch_specific_error_as_cli_error(self) -> None:
        """Test catching specific error as CLIError base class."""
        with pytest.raises(CLIError) as exc_info:
            raise UserNotFoundError("User not found")
        assert isinstance(exc_info.value, UserNotFoundError)
        assert exc_info.value.exit_code == ExitCode.USER_NOT_FOUND
