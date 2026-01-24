"""Unit tests for InMemoryUserRepository test double."""

import pytest

from mycli.domain import User, UserStatus, create_user
from tests.conftest import InMemoryUserRepository


class TestInMemoryUserRepository:
    """Test suite for InMemoryUserRepository."""

    def test_get_returns_none_for_missing_user(self, in_memory_repo: InMemoryUserRepository) -> None:
        """Test that get() returns None when user does not exist."""
        result = in_memory_repo.get("nonexistent-id")
        assert result is None

    def test_add_and_get_user(self, in_memory_repo: InMemoryUserRepository) -> None:
        """Test that add() stores user and get() retrieves it."""
        user = create_user("test@example.com")
        added = in_memory_repo.add(user)

        assert added is user
        retrieved = in_memory_repo.get(user.id)
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == user.email

    def test_get_by_email_returns_none_for_missing_email(
        self, in_memory_repo: InMemoryUserRepository
    ) -> None:
        """Test that get_by_email() returns None when email does not exist."""
        result = in_memory_repo.get_by_email("missing@example.com")
        assert result is None

    def test_get_by_email_finds_existing_user(self, in_memory_repo: InMemoryUserRepository) -> None:
        """Test that get_by_email() finds user by email."""
        user = create_user("test@example.com")
        in_memory_repo.add(user)

        retrieved = in_memory_repo.get_by_email("test@example.com")
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == user.email

    def test_list_all_returns_empty_list_initially(
        self, in_memory_repo: InMemoryUserRepository
    ) -> None:
        """Test that list_all() returns empty list when no users exist."""
        result = in_memory_repo.list_all()
        assert result == []

    def test_list_all_returns_all_users(self, in_memory_repo: InMemoryUserRepository) -> None:
        """Test that list_all() returns all added users."""
        user1 = create_user("user1@example.com")
        user2 = create_user("user2@example.com")
        in_memory_repo.add(user1)
        in_memory_repo.add(user2)

        all_users = in_memory_repo.list_all()
        assert len(all_users) == 2
        assert user1 in all_users
        assert user2 in all_users

    def test_delete_returns_false_for_missing_user(
        self, in_memory_repo: InMemoryUserRepository
    ) -> None:
        """Test that delete() returns False when user does not exist."""
        result = in_memory_repo.delete("nonexistent-id")
        assert result is False

    def test_delete_removes_existing_user(self, in_memory_repo: InMemoryUserRepository) -> None:
        """Test that delete() removes user and returns True."""
        user = create_user("test@example.com")
        in_memory_repo.add(user)

        result = in_memory_repo.delete(user.id)
        assert result is True

        # Verify user is actually removed
        retrieved = in_memory_repo.get(user.id)
        assert retrieved is None

    def test_save_is_no_op(self, in_memory_repo: InMemoryUserRepository) -> None:
        """Test that save() does nothing (no-op)."""
        # Should not raise any errors
        in_memory_repo.save()

    def test_add_overwrites_user_with_same_id(self, in_memory_repo: InMemoryUserRepository) -> None:
        """Test that adding a user with same ID overwrites the previous one."""
        user_id = "test-id"
        user1 = User(id=user_id, email="old@example.com")
        user2 = User(id=user_id, email="new@example.com")

        in_memory_repo.add(user1)
        in_memory_repo.add(user2)

        retrieved = in_memory_repo.get(user_id)
        assert retrieved is not None
        assert retrieved.email == "new@example.com"

    def test_isolation_between_instances(self) -> None:
        """Test that separate instances do not share state."""
        repo1 = InMemoryUserRepository()
        repo2 = InMemoryUserRepository()

        user = create_user("test@example.com")
        repo1.add(user)

        # repo2 should not see user from repo1
        assert repo2.get(user.id) is None

    def test_preserves_user_status(self, in_memory_repo: InMemoryUserRepository) -> None:
        """Test that user status is preserved when storing and retrieving."""
        user = User(id="test-id", email="test@example.com", status=UserStatus.INACTIVE)
        in_memory_repo.add(user)

        retrieved = in_memory_repo.get(user.id)
        assert retrieved is not None
        assert retrieved.status == UserStatus.INACTIVE
