"""Tests for repository protocol definition."""

from typing import Protocol, runtime_checkable

import pytest

from mycli.domain import User
from mycli.repository import UserRepository


def test_user_repository_is_protocol() -> None:
    """UserRepository should be a Protocol."""
    assert issubclass(UserRepository, Protocol)


def test_user_repository_is_runtime_checkable() -> None:
    """UserRepository should be runtime_checkable for isinstance checks."""
    # Should not raise AttributeError
    assert hasattr(UserRepository, "__protocol_attrs__")


def test_user_repository_has_get_method() -> None:
    """UserRepository protocol should define get method."""
    assert hasattr(UserRepository, "get")


def test_user_repository_has_get_by_email_method() -> None:
    """UserRepository protocol should define get_by_email method."""
    assert hasattr(UserRepository, "get_by_email")


def test_user_repository_has_add_method() -> None:
    """UserRepository protocol should define add method."""
    assert hasattr(UserRepository, "add")


def test_user_repository_has_list_all_method() -> None:
    """UserRepository protocol should define list_all method."""
    assert hasattr(UserRepository, "list_all")


def test_user_repository_has_delete_method() -> None:
    """UserRepository protocol should define delete method."""
    assert hasattr(UserRepository, "delete")


def test_user_repository_has_save_method() -> None:
    """UserRepository protocol should define save method."""
    assert hasattr(UserRepository, "save")


def test_concrete_implementation_matches_protocol() -> None:
    """A concrete implementation should match the protocol."""

    class ConcreteUserRepository:
        """Minimal concrete implementation for testing protocol compliance."""

        def get(self, user_id: str) -> User | None:
            return None

        def get_by_email(self, email: str) -> User | None:
            return None

        def add(self, user: User) -> User:
            return user

        def list_all(self) -> list[User]:
            return []

        def delete(self, user_id: str) -> bool:
            return False

        def save(self) -> None:
            pass

    repo = ConcreteUserRepository()
    # This should pass type checking if protocol is properly defined
    assert isinstance(repo, UserRepository)


def test_incomplete_implementation_fails_protocol() -> None:
    """An incomplete implementation should not match the protocol."""

    class IncompleteRepository:
        """Missing methods - should not satisfy protocol."""

        def get(self, user_id: str) -> User | None:
            return None

    repo = IncompleteRepository()
    # This should fail because not all methods are implemented
    assert not isinstance(repo, UserRepository)
