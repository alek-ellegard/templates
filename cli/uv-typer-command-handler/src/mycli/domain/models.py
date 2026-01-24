"""Domain models for the CLI application."""

import uuid
from enum import StrEnum


class UserStatus(StrEnum):
    """User status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class User:
    """User domain model."""

    def __init__(self, id: str, email: str, status: UserStatus = UserStatus.ACTIVE) -> None:
        """Initialize a User.

        Args:
            id: Unique identifier for the user
            email: User's email address
            status: User's status (defaults to ACTIVE)
        """
        self.id = id
        self.email = email
        self.status = status

    def to_dict(self) -> dict[str, str]:
        """Convert User to dictionary representation.

        Returns:
            Dictionary with id, email, and status (as string value)
        """
        return {
            "id": self.id,
            "email": self.email,
            "status": self.status.value,
        }


def create_user(email: str) -> User:
    """Create a new User with generated UUID.

    Args:
        email: User's email address

    Returns:
        New User instance with UUID id and ACTIVE status
    """
    return User(id=str(uuid.uuid4()), email=email)


def user_from_dict(data: dict[str, str]) -> User:
    """Reconstruct a User from dictionary representation.

    Args:
        data: Dictionary containing id, email, and status

    Returns:
        User instance reconstructed from data
    """
    return User(
        id=data["id"],
        email=data["email"],
        status=UserStatus(data["status"]),
    )
