"""Repository protocol definitions."""

from typing import Protocol, runtime_checkable

from mycli.domain import User


@runtime_checkable
class UserRepository(Protocol):
    """Protocol for user repository implementations.

    Defines the interface that all user repository implementations must follow.
    Using runtime_checkable allows isinstance checks for protocol compliance.
    """

    def get(self, user_id: str) -> User | None:
        """Retrieve a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User if found, None otherwise.
        """
        ...

    def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The User if found, None otherwise.
        """
        ...

    def add(self, user: User) -> User:
        """Add a new user to the repository.

        Args:
            user: The user to add.

        Returns:
            The added user (may include generated fields).
        """
        ...

    def list_all(self) -> list[User]:
        """Retrieve all users from the repository.

        Returns:
            A list of all users. Empty list if no users exist.
        """
        ...

    def delete(self, user_id: str) -> bool:
        """Delete a user from the repository.

        Args:
            user_id: The unique identifier of the user to delete.

        Returns:
            True if user was deleted, False if user was not found.
        """
        ...

    def save(self) -> None:
        """Persist any pending changes to storage.

        Implementations may batch changes and require explicit save calls,
        or may auto-save on each operation. This method ensures all changes
        are written to persistent storage.
        """
        ...
