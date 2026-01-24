"""Unit tests for TUI console module."""

from mycli.domain import User, UserStatus
from mycli.tui import TUI


def test_tui_initialization():
    """Test TUI initializes with Rich console instances."""
    tui = TUI()
    assert tui.console is not None
    assert tui.err_console is not None


def test_success_message(capsys):
    """Test success message displays with green checkmark."""
    tui = TUI()
    tui.success("Operation completed")
    captured = capsys.readouterr()
    assert "Operation completed" in captured.out
    assert "✓" in captured.out


def test_error_message(capsys):
    """Test error message displays with red X to stderr."""
    tui = TUI()
    tui.error("Something went wrong")
    captured = capsys.readouterr()
    assert "Something went wrong" in captured.err
    assert "✗" in captured.err


def test_info_message(capsys):
    """Test info message displays with blue info icon."""
    tui = TUI()
    tui.info("Processing request")
    captured = capsys.readouterr()
    assert "Processing request" in captured.out
    assert "ℹ" in captured.out


def test_user_detail(capsys):
    """Test user detail displays formatted user information."""
    tui = TUI()
    user = User(id="test-123", email="test@example.com", status=UserStatus.ACTIVE)
    tui.user_detail(user)
    captured = capsys.readouterr()
    assert "test-123" in captured.out
    assert "test@example.com" in captured.out
    assert "active" in captured.out.lower()


def test_user_table(capsys):
    """Test user table displays multiple users in tabular format."""
    tui = TUI()
    users = [
        User(id="id-1", email="user1@example.com", status=UserStatus.ACTIVE),
        User(id="id-2", email="user2@example.com", status=UserStatus.INACTIVE),
    ]
    tui.user_table(users)
    captured = capsys.readouterr()
    # Check that all user data appears in output
    assert "id-1" in captured.out
    assert "user1@example.com" in captured.out
    assert "id-2" in captured.out
    assert "user2@example.com" in captured.out
    assert "active" in captured.out.lower()
    assert "inactive" in captured.out.lower()


def test_user_table_empty(capsys):
    """Test user table handles empty list gracefully."""
    tui = TUI()
    tui.user_table([])
    captured = capsys.readouterr()
    # Should produce some output (even if empty table)
    assert captured.out is not None


def test_prompt(monkeypatch):
    """Test prompt gets user input."""
    tui = TUI()
    # Mock user input
    monkeypatch.setattr("builtins.input", lambda _: "test input")
    result = tui.prompt("Enter something:")
    assert result == "test input"


def test_confirm_yes(monkeypatch):
    """Test confirm returns True for yes responses."""
    tui = TUI()
    # Mock user input with 'y'
    monkeypatch.setattr("builtins.input", lambda _: "y")
    result = tui.confirm("Are you sure?")
    assert result is True


def test_confirm_no(monkeypatch):
    """Test confirm returns False for no responses."""
    tui = TUI()
    # Mock user input with 'n'
    monkeypatch.setattr("builtins.input", lambda _: "n")
    result = tui.confirm("Are you sure?")
    assert result is False


def test_confirm_uppercase_yes(monkeypatch):
    """Test confirm handles uppercase Y."""
    tui = TUI()
    monkeypatch.setattr("builtins.input", lambda _: "Y")
    result = tui.confirm("Are you sure?")
    assert result is True


def test_confirm_default_no(monkeypatch):
    """Test confirm defaults to False for other input."""
    tui = TUI()
    monkeypatch.setattr("builtins.input", lambda _: "maybe")
    result = tui.confirm("Are you sure?")
    assert result is False
