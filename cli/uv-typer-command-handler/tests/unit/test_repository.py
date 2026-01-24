"""Unit tests for JsonUserRepository."""

import json
from pathlib import Path

import pytest

from mycli.domain.models import UserStatus, create_user
from mycli.exceptions import RepositoryError
from mycli.repository.json import JsonUserRepository


def test_json_repo_creates_file(tmp_path: Path) -> None:
    """Test that repository creates a JSON file when adding a user."""
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo.add(user)
    assert path.exists()


def test_json_repo_persists_data(tmp_path: Path) -> None:
    """Test that data persists across repository instances."""
    path = tmp_path / "users.json"

    # Create first repository and add user
    repo1 = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo1.add(user)

    # Create second repository and verify data is loaded
    repo2 = JsonUserRepository(path)
    loaded = repo2.get(user.id)
    assert loaded is not None
    assert loaded.email == "test@example.com"
    assert loaded.status == UserStatus.ACTIVE


def test_json_repo_list_all(tmp_path: Path) -> None:
    """Test that list_all returns all users."""
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)

    user1 = create_user("a@example.com")
    user2 = create_user("b@example.com")
    repo.add(user1)
    repo.add(user2)

    users = repo.list_all()
    assert len(users) == 2
    emails = {u.email for u in users}
    assert emails == {"a@example.com", "b@example.com"}


def test_json_repo_delete(tmp_path: Path) -> None:
    """Test that delete removes user and returns True."""
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo.add(user)

    # Delete should return True and remove user
    assert repo.delete(user.id) is True
    assert repo.get(user.id) is None

    # Delete non-existent should return False
    assert repo.delete(user.id) is False


def test_json_repo_get_by_email(tmp_path: Path) -> None:
    """Test that get_by_email finds user by email address."""
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo.add(user)

    found = repo.get_by_email("test@example.com")
    assert found is not None
    assert found.id == user.id
    assert found.email == user.email

    # Non-existent email should return None
    not_found = repo.get_by_email("nonexistent@example.com")
    assert not_found is None


def test_json_repo_initializes_empty_on_nonexistent_file(tmp_path: Path) -> None:
    """Test that repository initializes with empty data when file doesn't exist."""
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)

    assert repo.list_all() == []
    assert not path.exists()  # File not created until first save


def test_json_repo_raises_on_corrupt_json(tmp_path: Path) -> None:
    """Test that repository raises RepositoryError on corrupt JSON."""
    path = tmp_path / "users.json"
    path.write_text("not valid json {")

    with pytest.raises(RepositoryError) as exc_info:
        JsonUserRepository(path)

    assert "Failed to load data" in str(exc_info.value)


def test_json_repo_raises_on_invalid_data_structure(tmp_path: Path) -> None:
    """Test that repository raises RepositoryError on invalid data structure."""
    path = tmp_path / "users.json"
    # Missing required fields
    path.write_text(json.dumps({"user-id": {"email": "test@example.com"}}))

    with pytest.raises(RepositoryError) as exc_info:
        JsonUserRepository(path)

    assert "Failed to load data" in str(exc_info.value)


def test_json_repo_creates_parent_directories(tmp_path: Path) -> None:
    """Test that repository creates parent directories when saving."""
    path = tmp_path / "nested" / "dir" / "users.json"
    repo = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo.add(user)

    assert path.exists()
    assert path.parent.exists()
