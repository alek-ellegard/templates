"""Unit tests for handlers."""

import pytest

from mycli.exceptions import UserExistsError, UserNotFoundError
from mycli.handlers.users import UserHandler


def test_create_user(in_memory_repo):
    """Test creating a user with email."""
    handler = UserHandler(in_memory_repo)
    user = handler.create("test@example.com")
    assert user.email == "test@example.com"
    assert user.id is not None


def test_create_duplicate_user_raises(in_memory_repo):
    """Test that creating duplicate user raises UserExistsError."""
    handler = UserHandler(in_memory_repo)
    handler.create("test@example.com")
    with pytest.raises(UserExistsError):
        handler.create("test@example.com")


def test_get_user(in_memory_repo):
    """Test getting an existing user by ID."""
    handler = UserHandler(in_memory_repo)
    user = handler.create("test@example.com")
    retrieved = handler.get(user.id)
    assert retrieved.id == user.id
    assert retrieved.email == user.email


def test_get_nonexistent_user_raises(in_memory_repo):
    """Test that getting nonexistent user raises UserNotFoundError."""
    handler = UserHandler(in_memory_repo)
    with pytest.raises(UserNotFoundError):
        handler.get("nonexistent-id")


def test_list_users_empty(in_memory_repo):
    """Test listing users returns empty list when no users exist."""
    handler = UserHandler(in_memory_repo)
    users = handler.list()
    assert users == []


def test_list_users(in_memory_repo):
    """Test listing users returns list of created users."""
    handler = UserHandler(in_memory_repo)
    user1 = handler.create("user1@example.com")
    user2 = handler.create("user2@example.com")
    users = handler.list()
    assert len(users) == 2
    assert user1 in users
    assert user2 in users


def test_delete_user(in_memory_repo):
    """Test successfully deleting a user."""
    handler = UserHandler(in_memory_repo)
    user = handler.create("test@example.com")
    handler.delete(user.id)
    with pytest.raises(UserNotFoundError):
        handler.get(user.id)


def test_delete_nonexistent_user_raises(in_memory_repo):
    """Test that deleting nonexistent user raises UserNotFoundError."""
    handler = UserHandler(in_memory_repo)
    with pytest.raises(UserNotFoundError):
        handler.delete("nonexistent-id")
