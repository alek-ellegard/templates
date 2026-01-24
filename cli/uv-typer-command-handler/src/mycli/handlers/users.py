"""User handlers for application logic."""

from mycli.domain.models import User, create_user
from mycli.exceptions import UserExistsError
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
