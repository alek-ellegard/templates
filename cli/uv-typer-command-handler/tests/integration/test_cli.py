"""Integration tests for CLI commands."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mycli.commands.users import app as users_app


def test_create_user_cli(runner: CliRunner, tmp_data_dir: Path) -> None:
    """Test creating a user via CLI creates user and saves to JSON."""
    repo_path = tmp_data_dir / "users.json"

    # Create the command with repo_path in context
    result = runner.invoke(
        users_app,
        ["create", "test@example.com"],
        obj={"repo_path": repo_path}
    )

    assert result.exit_code == 0
    assert "Created user" in result.stdout
    assert "test@example.com" in result.stdout

    # Verify user was persisted to JSON
    assert repo_path.exists()
    data = json.loads(repo_path.read_text())
    assert len(data) == 1
    user_data = list(data.values())[0]
    assert user_data["email"] == "test@example.com"
    assert user_data["status"] == "active"


def test_create_duplicate_user_cli(runner: CliRunner, tmp_data_dir: Path) -> None:
    """Test creating duplicate user via CLI shows error."""
    repo_path = tmp_data_dir / "users.json"

    # Create first user
    result1 = runner.invoke(
        users_app,
        ["create", "test@example.com"],
        obj={"repo_path": repo_path}
    )
    assert result1.exit_code == 0

    # Try to create duplicate
    result2 = runner.invoke(
        users_app,
        ["create", "test@example.com"],
        obj={"repo_path": repo_path}
    )

    assert result2.exit_code != 0
    # Error messages go to stderr
    assert "already exists" in result2.stderr
