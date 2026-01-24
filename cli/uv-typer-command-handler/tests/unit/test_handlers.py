"""Unit tests for handlers."""

import pytest

from mycli.exceptions import UserExistsError
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
