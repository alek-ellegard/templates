import pytest
from pathlib import Path
from typer.testing import CliRunner

from mycli.domain.models import User


class InMemoryUserRepository:
    """Test double for UserRepository."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def add(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def list_all(self) -> list[User]:
        return list(self._users.values())

    def delete(self, user_id: str) -> bool:
        if user_id not in self._users:
            return False
        del self._users[user_id]
        return True

    def save(self) -> None:
        pass  # No-op for in-memory


@pytest.fixture
def in_memory_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    return tmp_path / "mycli"
