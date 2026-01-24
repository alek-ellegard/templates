import pytest
from typer.testing import CliRunner

from mycli.main import app


def test_users_list_empty(runner: CliRunner, tmp_data_dir):
    result = runner.invoke(app, ["--data-dir", str(tmp_data_dir), "users", "list"])
    assert result.exit_code == 0
    assert "No users found" in result.stdout


def test_users_create(runner: CliRunner, tmp_data_dir):
    result = runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    assert result.exit_code == 0
    assert "Created user" in result.stdout


def test_users_create_and_list(runner: CliRunner, tmp_data_dir):
    runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    result = runner.invoke(app, ["--data-dir", str(tmp_data_dir), "users", "list"])
    assert result.exit_code == 0
    assert "test@example.com" in result.stdout


def test_users_create_duplicate_fails(runner: CliRunner, tmp_data_dir):
    runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    result = runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    assert result.exit_code != 0


def test_users_delete_with_force(runner: CliRunner, tmp_data_dir):
    result = runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    assert result.exit_code == 0, f"Create failed: {result.stdout}"

    # Extract user ID from output
    # The output format is "  ID:     <uuid>"
    lines = result.stdout.split("\n")
    id_lines = [l for l in lines if "ID:" in l]
    assert id_lines, f"No ID line found in output: {result.stdout}"
    user_id = id_lines[0].split(":")[-1].strip()

    result = runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "delete", user_id, "--force"]
    )
    assert result.exit_code == 0
    assert "Deleted user" in result.stdout
