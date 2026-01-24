"""User handlers for application logic."""

from mycli.domain.models import User, create_user
from mycli.exceptions import UserExistsError, UserNotFoundError
from mycli.repository.base import UserRepository


class UserHandler:
    """Handler for user-related operations."""

    def __init__(self, repository: UserRepository) -> None:
        """Initialize UserHandler.

        Args:
            repository: Repository implementation for user persistence
        """
        self.repository = repository

    def create(self, email: str) -> User:
        """Create a new user.

        Args:
            email: Email address for the new user

        Returns:
            The newly created User

        Raises:
            UserExistsError: If a user with the given email already exists
        """
        existing = self.repository.get_by_email(email)
        if existing is not None:
            raise UserExistsError(f"User with email {email} already exists")
        user = create_user(email)
        return self.repository.add(user)

    def get(self, user_id: str) -> User:
        """Get a user by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            The User with the given ID

        Raises:
            UserNotFoundError: If no user with the given ID exists
        """
        user = self.repository.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    def list(self) -> list[User]:
        """Get all users.

        Returns:
            List of all users. Empty list if no users exist.
        """
        return self.repository.list_all()

    def delete(self, user_id: str) -> None:
        """Delete a user by ID.

        Args:
            user_id: ID of the user to delete

        Raises:
            UserNotFoundError: If no user with the given ID exists
        """
        deleted = self.repository.delete(user_id)
        if not deleted:
            raise UserNotFoundError(f"User {user_id} not found")
        self.repository.save()
