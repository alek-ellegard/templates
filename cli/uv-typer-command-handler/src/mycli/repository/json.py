"""JSON file-based repository implementation."""

import json
from pathlib import Path

from mycli.domain.models import User, user_from_dict
from mycli.exceptions import RepositoryError


class JsonUserRepository:
    """JSON file-based repository for User persistence.

    Stores users in a JSON file as a dictionary mapping user IDs to user data.
    Automatically saves changes to disk on mutations (add, delete).
    """

    def __init__(self, path: Path) -> None:
        """Initialize the JSON repository.

        Args:
            path: Path to the JSON file for storing users.

        Raises:
            RepositoryError: If the existing file contains invalid JSON or data.
        """
        self.path = path
        self._users: dict[str, User] = {}
        self._load()

    def _load(self) -> None:
        """Load users from the JSON file.

        If the file doesn't exist, initializes with empty data.

        Raises:
            RepositoryError: If JSON is malformed or data structure is invalid.
        """
        if not self.path.exists():
            self._users = {}
            return

        try:
            data = json.loads(self.path.read_text())
            self._users = {uid: user_from_dict(udata) for uid, udata in data.items()}
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RepositoryError(f"Failed to load data: {e}") from e

    def save(self) -> None:
        """Persist current user data to the JSON file.

        Creates parent directories if they don't exist.
        Writes JSON with 2-space indentation for readability.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {uid: u.to_dict() for uid, u in self._users.items()}
        self.path.write_text(json.dumps(data, indent=2))

    def get(self, user_id: str) -> User | None:
        """Retrieve a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User if found, None otherwise.
        """
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The User if found, None otherwise.
        """
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def add(self, user: User) -> User:
        """Add a new user to the repository.

        Args:
            user: The user to add.

        Returns:
            The added user (unchanged).
        """
        self._users[user.id] = user
        self.save()
        return user

    def list_all(self) -> list[User]:
        """Retrieve all users from the repository.

        Returns:
            A list of all users. Empty list if no users exist.
        """
        return list(self._users.values())

    def delete(self, user_id: str) -> bool:
        """Delete a user from the repository.

        Args:
            user_id: The unique identifier of the user to delete.

        Returns:
            True if user was deleted, False if user was not found.
        """
        if user_id not in self._users:
            return False
        del self._users[user_id]
        self.save()
        return True
