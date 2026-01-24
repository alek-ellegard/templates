"""Unit tests for domain models."""

import uuid

from mycli.domain.models import User, UserStatus, create_user, user_from_dict


def test_user_status_enum_values() -> None:
    """Test UserStatus enum has correct values."""
    assert UserStatus.ACTIVE == "active"
    assert UserStatus.INACTIVE == "inactive"
    assert isinstance(UserStatus.ACTIVE, str)
    assert isinstance(UserStatus.INACTIVE, str)


def test_user_init_with_defaults() -> None:
    """Test User initialization with default status."""
    user = User(id="test-id", email="test@example.com")
    assert user.id == "test-id"
    assert user.email == "test@example.com"
    assert user.status == UserStatus.ACTIVE


def test_user_init_with_explicit_status() -> None:
    """Test User initialization with explicit status."""
    user = User(id="test-id", email="test@example.com", status=UserStatus.INACTIVE)
    assert user.id == "test-id"
    assert user.email == "test@example.com"
    assert user.status == UserStatus.INACTIVE


def test_user_to_dict_active() -> None:
    """Test User.to_dict() with active status."""
    user = User(id="test-id", email="test@example.com", status=UserStatus.ACTIVE)
    data = user.to_dict()
    assert data == {
        "id": "test-id",
        "email": "test@example.com",
        "status": "active",
    }


def test_user_to_dict_inactive() -> None:
    """Test User.to_dict() with inactive status."""
    user = User(id="test-id", email="test@example.com", status=UserStatus.INACTIVE)
    data = user.to_dict()
    assert data == {
        "id": "test-id",
        "email": "test@example.com",
        "status": "inactive",
    }


def test_create_user_generates_uuid() -> None:
    """Test create_user generates a valid UUID for id."""
    user = create_user(email="test@example.com")
    # Should be able to parse as UUID
    uuid.UUID(user.id)
    assert user.email == "test@example.com"
    assert user.status == UserStatus.ACTIVE


def test_create_user_generates_unique_ids() -> None:
    """Test create_user generates unique IDs for different users."""
    user1 = create_user(email="test1@example.com")
    user2 = create_user(email="test2@example.com")
    assert user1.id != user2.id


def test_user_from_dict_active() -> None:
    """Test user_from_dict reconstructs User with active status."""
    data = {
        "id": "test-id",
        "email": "test@example.com",
        "status": "active",
    }
    user = user_from_dict(data)
    assert user.id == "test-id"
    assert user.email == "test@example.com"
    assert user.status == UserStatus.ACTIVE


def test_user_from_dict_inactive() -> None:
    """Test user_from_dict reconstructs User with inactive status."""
    data = {
        "id": "test-id",
        "email": "test@example.com",
        "status": "inactive",
    }
    user = user_from_dict(data)
    assert user.id == "test-id"
    assert user.email == "test@example.com"
    assert user.status == UserStatus.INACTIVE


def test_user_roundtrip() -> None:
    """Test User can be serialized and deserialized without data loss."""
    original = User(id="test-id", email="test@example.com", status=UserStatus.INACTIVE)
    data = original.to_dict()
    reconstructed = user_from_dict(data)
    assert reconstructed.id == original.id
    assert reconstructed.email == original.email
    assert reconstructed.status == original.status
