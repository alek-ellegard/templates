# PRD: Modern Python CLI Template (Astral Stack)

## 1. Project Overview

**Goal:** Create a robust, reusable Python CLI template using pure `uv` as package manager.

**Architecture:** Layered CLI architecture with clear separation of concerns.

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Interface | `tui/` | Rich output, interactive prompts |
| Commands | `commands/` | Thin CLI parsing, delegate to handlers |
| Handlers | `handlers/` | Application logic, orchestration |
| Domain | `domain/` | Pure models, business rules |
| Infrastructure | `repository/` | Data persistence |

---

## 2. Design Principles

| Principle | Description |
|-----------|-------------|
| No backward compatibility | Clean breaks allowed, no legacy support |
| Tracer bullet | Features implemented as vertical slices through all layers |
| TDD | Write test first, then implementation |
| Native Python only | No dataclasses, no pydantic, no @classmethod |
| Explicit types | StrEnum for enums, `T \| None` not `Optional[T]` |
| Simple classes | Constructor + instance methods only |

---

## 3. Technical Stack

| Tool | Purpose |
|------|---------|
| `uv` | Package management, venv, script runner |
| `ty` | Type checking (Astral) |
| `ruff` | Linting + formatting |
| `pytest` | Testing |
| `typer` | CLI framework |
| `rich` | Terminal output + interactive prompts |

---

## 4. Directory Structure

```
cli-template/
├── pyproject.toml
├── Makefile
├── README.md
├── CLAUDE.md              # AI agent coding guidelines
├── src/
│   └── mycli/
│       ├── __init__.py
│       ├── main.py        # Entry point, Typer app, DI wiring
│       ├── config.py      # Settings, AppContext container
│       ├── exceptions.py  # Domain exceptions with exit codes
│       │
│       ├── tui/
│       │   ├── __init__.py
│       │   └── console.py # Output formatting, interactive prompts
│       │
│       ├── commands/
│       │   ├── __init__.py
│       │   └── users.py   # CLI command definitions (thin)
│       │
│       ├── handlers/
│       │   ├── __init__.py
│       │   └── users.py   # Application logic
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   └── models.py  # User, etc. (native classes)
│       │
│       └── repository/
│           ├── __init__.py
│           ├── base.py    # UserRepository protocol
│           └── json.py    # JsonUserRepository implementation
│
└── tests/
    ├── __init__.py
    ├── conftest.py        # Fixtures: mock repos, temp files
    ├── unit/
    │   ├── __init__.py
    │   ├── test_models.py
    │   ├── test_handlers.py
    │   └── test_repository.py
    └── integration/
        ├── __init__.py
        └── test_cli.py
```

---

## 5. Data Flow

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ commands/users.py                                       │
│   - Parse CLI args                                      │
│   - Get handler from ctx.obj                            │
│   - Call handler method                                 │
│   - Pass result to TUI                                  │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ handlers/users.py                                       │
│   - Validate business rules                             │
│   - Call repository methods                             │
│   - Return domain objects or raise exceptions           │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ repository/json.py                                      │
│   - Read/write JSON file                                │
│   - Map JSON ↔ domain objects                           │
│   - Raise RepositoryError on failures                   │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ tui/console.py                                          │
│   - Format output (tables, panels)                      │
│   - Display errors                                      │
│   - Interactive prompts (confirm, select, input)        │
└─────────────────────────────────────────────────────────┘
    │
    ▼
stdout / stderr
```

---

## 6. Core Components

### 6.1 Domain Models (`domain/models.py`)

Native Python classes. No decorators. Constructor + instance methods only.

```python
from enum import StrEnum
import uuid


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User:
    def __init__(self, id: str, email: str, status: UserStatus) -> None:
        self.id = id
        self.email = email
        self.status = status

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "email": self.email,
            "status": self.status.value,
        }


def create_user(email: str) -> User:
    """Factory function for creating new users."""
    return User(
        id=str(uuid.uuid4()),
        email=email,
        status=UserStatus.ACTIVE,
    )


def user_from_dict(data: dict[str, str]) -> User:
    """Factory function for deserializing users."""
    return User(
        id=data["id"],
        email=data["email"],
        status=UserStatus(data["status"]),
    )
```

### 6.2 Exceptions (`exceptions.py`)

```python
from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    USER_NOT_FOUND = 10
    USER_EXISTS = 11
    REPOSITORY_ERROR = 20
    VALIDATION_ERROR = 30


class CLIError(Exception):
    def __init__(self, message: str, exit_code: ExitCode) -> None:
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)


class UserNotFoundError(CLIError):
    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message, ExitCode.USER_NOT_FOUND)


class UserExistsError(CLIError):
    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message, ExitCode.USER_EXISTS)


class RepositoryError(CLIError):
    def __init__(self, message: str = "Repository operation failed") -> None:
        super().__init__(message, ExitCode.REPOSITORY_ERROR)


class ValidationError(CLIError):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, ExitCode.VALIDATION_ERROR)
```

### 6.3 Repository Protocol (`repository/base.py`)

```python
from typing import Protocol

from mycli.domain.models import User


class UserRepository(Protocol):
    def get(self, user_id: str) -> User | None: ...
    def get_by_email(self, email: str) -> User | None: ...
    def add(self, user: User) -> User: ...
    def list_all(self) -> list[User]: ...
    def delete(self, user_id: str) -> bool: ...
    def save(self) -> None: ...
```

### 6.4 JSON Repository (`repository/json.py`)

```python
import json
from pathlib import Path

from mycli.domain.models import User, user_from_dict
from mycli.exceptions import RepositoryError


class JsonUserRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._users: dict[str, User] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self._users = {}
            return
        try:
            data = json.loads(self.path.read_text())
            self._users = {
                uid: user_from_dict(udata) 
                for uid, udata in data.items()
            }
        except (json.JSONDecodeError, KeyError) as e:
            raise RepositoryError(f"Failed to load data: {e}") from e

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {uid: u.to_dict() for uid, u in self._users.items()}
        self.path.write_text(json.dumps(data, indent=2))

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def add(self, user: User) -> User:
        self._users[user.id] = user
        self.save()
        return user

    def list_all(self) -> list[User]:
        return list(self._users.values())

    def delete(self, user_id: str) -> bool:
        if user_id not in self._users:
            return False
        del self._users[user_id]
        self.save()
        return True
```

### 6.5 Handlers (`handlers/users.py`)

```python
from mycli.domain.models import User, create_user
from mycli.repository.base import UserRepository
from mycli.exceptions import UserExistsError, UserNotFoundError


class UserHandler:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create(self, email: str) -> User:
        existing = self.repository.get_by_email(email)
        if existing is not None:
            raise UserExistsError(f"User with email {email} already exists")
        user = create_user(email)
        return self.repository.add(user)

    def list(self) -> list[User]:
        return self.repository.list_all()

    def get(self, user_id: str) -> User:
        user = self.repository.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    def delete(self, user_id: str) -> None:
        deleted = self.repository.delete(user_id)
        if not deleted:
            raise UserNotFoundError(f"User {user_id} not found")
```

### 6.6 TUI Console (`tui/console.py`)

```python
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from mycli.domain.models import User


class TUI:
    def __init__(self) -> None:
        self.console = Console()
        self.err_console = Console(stderr=True)

    def success(self, message: str) -> None:
        self.console.print(f"[green]✓[/green] {message}")

    def error(self, message: str) -> None:
        self.err_console.print(f"[red]✗[/red] {message}")

    def info(self, message: str) -> None:
        self.console.print(f"[blue]ℹ[/blue] {message}")

    def user_table(self, users: list[User]) -> None:
        table = Table(title="Users")
        table.add_column("ID", style="dim")
        table.add_column("Email")
        table.add_column("Status")
        for user in users:
            table.add_row(user.id, user.email, user.status.value)
        self.console.print(table)

    def user_detail(self, user: User) -> None:
        self.console.print(f"[bold]ID:[/bold] {user.id}")
        self.console.print(f"[bold]Email:[/bold] {user.email}")
        self.console.print(f"[bold]Status:[/bold] {user.status.value}")

    def prompt(self, message: str, default: str = "") -> str:
        return Prompt.ask(message, default=default)

    def confirm(self, message: str, default: bool = False) -> bool:
        return Confirm.ask(message, default=default)
```

### 6.7 Commands (`commands/users.py`)

```python
import typer
from typing import Annotated

from mycli.handlers.users import UserHandler
from mycli.tui.console import TUI

app = typer.Typer(help="User management commands")


def get_handler(ctx: typer.Context) -> UserHandler:
    return ctx.obj["user_handler"]


def get_tui(ctx: typer.Context) -> TUI:
    return ctx.obj["tui"]


@app.command("create")
def create(
    ctx: typer.Context,
    email: Annotated[str, typer.Argument(help="User email address")],
) -> None:
    """Create a new user."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    user = handler.create(email)
    tui.success(f"Created user {user.id}")
    tui.user_detail(user)


@app.command("list")
def list_users(ctx: typer.Context) -> None:
    """List all users."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    users = handler.list()
    if not users:
        tui.info("No users found")
        return
    tui.user_table(users)


@app.command("get")
def get(
    ctx: typer.Context,
    user_id: Annotated[str, typer.Argument(help="User ID")],
) -> None:
    """Get user by ID."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    user = handler.get(user_id)
    tui.user_detail(user)


@app.command("delete")
def delete(
    ctx: typer.Context,
    user_id: Annotated[str, typer.Argument(help="User ID")],
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Delete a user."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    if not force:
        if not tui.confirm(f"Delete user {user_id}?"):
            tui.info("Cancelled")
            raise typer.Exit(0)
    handler.delete(user_id)
    tui.success(f"Deleted user {user_id}")
```

### 6.8 Config (`config.py`)

```python
from pathlib import Path


class AppConfig:
    def __init__(self, data_dir: Path | None = None) -> None:
        if data_dir is None:
            data_dir = Path.home() / ".mycli"
        self.data_dir = data_dir
        self.users_file = self.data_dir / "users.json"


class AppContext:
    def __init__(
        self,
        config: AppConfig,
        user_handler: "UserHandler",
        tui: "TUI",
    ) -> None:
        self.config = config
        self.user_handler = user_handler
        self.tui = tui

    def to_dict(self) -> dict:
        return {
            "config": self.config,
            "user_handler": self.user_handler,
            "tui": self.tui,
        }
```

### 6.9 Main Entry Point (`main.py`)

```python
import typer
from pathlib import Path
from typing import Annotated

from mycli.config import AppConfig, AppContext
from mycli.repository.json import JsonUserRepository
from mycli.handlers.users import UserHandler
from mycli.tui.console import TUI
from mycli.commands import users
from mycli.exceptions import CLIError

app = typer.Typer(
    name="mycli",
    help="A modern CLI template",
    no_args_is_help=True,
)

app.add_typer(users.app, name="users")


@app.callback()
def main(
    ctx: typer.Context,
    data_dir: Annotated[
        Path | None,
        typer.Option("--data-dir", "-d", help="Data directory path"),
    ] = None,
) -> None:
    """Initialize application context."""
    config = AppConfig(data_dir)
    repository = JsonUserRepository(config.users_file)
    handler = UserHandler(repository)
    tui = TUI()
    context = AppContext(config, handler, tui)
    ctx.obj = context.to_dict()


def run() -> None:
    try:
        app()
    except CLIError as e:
        tui = TUI()
        tui.error(e.message)
        raise typer.Exit(e.exit_code)


if __name__ == "__main__":
    run()
```

---

## 7. Configuration Files

### 7.1 `pyproject.toml`

```toml
[project]
name = "mycli"
version = "0.1.0"
description = "A modern CLI template using uv"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
]

[project.scripts]
mycli = "mycli.main:run"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "ruff>=0.4.0",
    "ty",
]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

### 7.2 `Makefile`

```makefile
.PHONY: install format lint typecheck test run ci clean

install:
	uv sync

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

typecheck:
	uv run ty check src

test:
	uv run pytest tests -v

run:
	uv run mycli

ci: install lint typecheck test

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

### 7.3 `CLAUDE.md`

```markdown
# CLAUDE.md - AI Agent Coding Guidelines

## Architecture

```
commands/ → handlers/ → repository/
    ↓           ↓            ↓
   tui/      domain/      (JSON)
```

Commands are thin. Handlers contain logic. Repository handles persistence.

## Design Principles

### No Backward Compatibility
- Clean breaks allowed
- No deprecation warnings
- No legacy support code

### Tracer Bullet Implementation
- New feature = vertical slice through ALL layers
- Start with test (TDD)
- Then: model → repository → handler → command → tui
- Simple first, enhance later

### Native Python Only
```python
# YES
class User:
    def __init__(self, id: str, email: str) -> None:
        self.id = id
        self.email = email

# NO - dataclass
@dataclass
class User:
    id: str
    email: str

# NO - pydantic
class User(BaseModel):
    id: str
    email: str

# NO - classmethod
@classmethod
def from_dict(cls, data: dict) -> "User":
    ...

# YES - factory function
def user_from_dict(data: dict[str, str]) -> User:
    return User(id=data["id"], email=data["email"])
```

### Explicit Types
```python
# YES
def get(self, id: str) -> User | None:

# NO
def get(self, id: str) -> Optional[User]:

# YES - StrEnum
class Status(StrEnum):
    ACTIVE = "active"

# NO - plain strings
status: str = "active"
```

### TDD Workflow
1. Write failing test
2. Implement minimum code to pass
3. Refactor
4. Repeat

## Error Handling

Exceptions bubble up from repository → handler → command → main.

```python
# In handler
if user is None:
    raise UserNotFoundError(f"User {id} not found")

# In main.py
except CLIError as e:
    tui.error(e.message)
    raise typer.Exit(e.exit_code)
```

## Adding a New Feature

Example: Add "user update" command

1. **Test first** (`tests/unit/test_handlers.py`):
```python
def test_update_user_email():
    repo = InMemoryUserRepository()
    handler = UserHandler(repo)
    user = handler.create("old@example.com")
    updated = handler.update(user.id, email="new@example.com")
    assert updated.email == "new@example.com"
```

2. **Domain** (if needed): Add any new models/enums

3. **Repository** (`repository/base.py`):
```python
def update(self, user: User) -> User: ...
```

4. **Repository impl** (`repository/json.py`):
```python
def update(self, user: User) -> User:
    self._users[user.id] = user
    self.save()
    return user
```

5. **Handler** (`handlers/users.py`):
```python
def update(self, user_id: str, email: str | None = None) -> User:
    user = self.get(user_id)
    if email is not None:
        user.email = email
    return self.repository.update(user)
```

6. **Command** (`commands/users.py`):
```python
@app.command("update")
def update(ctx: typer.Context, user_id: str, email: str) -> None:
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    user = handler.update(user_id, email=email)
    tui.success(f"Updated user {user_id}")
```

7. **Integration test** (`tests/integration/test_cli.py`):
```python
def test_update_user_cli(runner, tmp_path):
    # setup
    result = runner.invoke(app, ["users", "update", user_id, "--email", "new@test.com"])
    assert result.exit_code == 0
```

## File Naming

| Layer | Naming |
|-------|--------|
| Commands | `commands/{resource}.py` |
| Handlers | `handlers/{resource}.py` |
| Repository | `repository/{implementation}.py` |
| Domain | `domain/models.py` |
| TUI | `tui/console.py` |

## Testing

- Unit tests: test handlers with mock/in-memory repository
- Integration tests: test CLI with CliRunner and temp files
- No mocking of domain models
```

---

## 8. Testing

### 8.1 `tests/conftest.py`

```python
import pytest
from pathlib import Path
from typer.testing import CliRunner

from mycli.domain.models import User, UserStatus
from mycli.repository.base import UserRepository


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
```

### 8.2 `tests/unit/test_handlers.py`

```python
import pytest
from mycli.handlers.users import UserHandler
from mycli.exceptions import UserExistsError, UserNotFoundError


def test_create_user(in_memory_repo):
    handler = UserHandler(in_memory_repo)
    user = handler.create("test@example.com")
    assert user.email == "test@example.com"
    assert user.id is not None


def test_create_duplicate_user_raises(in_memory_repo):
    handler = UserHandler(in_memory_repo)
    handler.create("test@example.com")
    with pytest.raises(UserExistsError):
        handler.create("test@example.com")


def test_list_users_empty(in_memory_repo):
    handler = UserHandler(in_memory_repo)
    users = handler.list()
    assert users == []


def test_list_users(in_memory_repo):
    handler = UserHandler(in_memory_repo)
    handler.create("a@example.com")
    handler.create("b@example.com")
    users = handler.list()
    assert len(users) == 2


def test_get_user(in_memory_repo):
    handler = UserHandler(in_memory_repo)
    created = handler.create("test@example.com")
    fetched = handler.get(created.id)
    assert fetched.email == created.email


def test_get_nonexistent_user_raises(in_memory_repo):
    handler = UserHandler(in_memory_repo)
    with pytest.raises(UserNotFoundError):
        handler.get("nonexistent-id")


def test_delete_user(in_memory_repo):
    handler = UserHandler(in_memory_repo)
    user = handler.create("test@example.com")
    handler.delete(user.id)
    assert handler.list() == []


def test_delete_nonexistent_user_raises(in_memory_repo):
    handler = UserHandler(in_memory_repo)
    with pytest.raises(UserNotFoundError):
        handler.delete("nonexistent-id")
```

### 8.3 `tests/unit/test_repository.py`

```python
import pytest
from pathlib import Path

from mycli.repository.json import JsonUserRepository
from mycli.domain.models import User, UserStatus, create_user


def test_json_repo_creates_file(tmp_path: Path):
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo.add(user)
    assert path.exists()


def test_json_repo_persists_data(tmp_path: Path):
    path = tmp_path / "users.json"
    repo1 = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo1.add(user)

    repo2 = JsonUserRepository(path)
    loaded = repo2.get(user.id)
    assert loaded is not None
    assert loaded.email == "test@example.com"


def test_json_repo_list_all(tmp_path: Path):
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)
    repo.add(create_user("a@example.com"))
    repo.add(create_user("b@example.com"))
    users = repo.list_all()
    assert len(users) == 2


def test_json_repo_delete(tmp_path: Path):
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo.add(user)
    assert repo.delete(user.id) is True
    assert repo.get(user.id) is None


def test_json_repo_get_by_email(tmp_path: Path):
    path = tmp_path / "users.json"
    repo = JsonUserRepository(path)
    user = create_user("test@example.com")
    repo.add(user)
    found = repo.get_by_email("test@example.com")
    assert found is not None
    assert found.id == user.id
```

### 8.4 `tests/integration/test_cli.py`

```python
import pytest
from typer.testing import CliRunner

from mycli.main import app


def test_users_list_empty(runner: CliRunner, tmp_data_dir):
    result = runner.invoke(app, ["--data-dir", str(tmp_data_dir), "users", "list"])
    assert result.exit_code == 0
    assert "No users found" in result.stdout


def test_users_create(runner: CliRunner, tmp_data_dir):
    result = runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    assert result.exit_code == 0
    assert "Created user" in result.stdout


def test_users_create_and_list(runner: CliRunner, tmp_data_dir):
    runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    result = runner.invoke(app, ["--data-dir", str(tmp_data_dir), "users", "list"])
    assert result.exit_code == 0
    assert "test@example.com" in result.stdout


def test_users_create_duplicate_fails(runner: CliRunner, tmp_data_dir):
    runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    result = runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    assert result.exit_code != 0


def test_users_delete_with_force(runner: CliRunner, tmp_data_dir):
    result = runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "create", "test@example.com"]
    )
    # Extract user ID from output (simplified)
    lines = result.stdout.split("\n")
    id_line = [l for l in lines if "ID:" in l][0]
    user_id = id_line.split("ID:")[1].strip()

    result = runner.invoke(
        app, ["--data-dir", str(tmp_data_dir), "users", "delete", user_id, "--force"]
    )
    assert result.exit_code == 0
    assert "Deleted user" in result.stdout
```

---

## 9. Implementation Order

Follow tracer bullet approach:

1. **Setup**
   - Create directory structure
   - Write `pyproject.toml`
   - Write `Makefile`
   - Run `make install`

2. **Domain layer**
   - Write `test_models.py` (TDD)
   - Implement `domain/models.py`
   - Implement `exceptions.py`

3. **Repository layer**
   - Write `test_repository.py` (TDD)
   - Implement `repository/base.py`
   - Implement `repository/json.py`

4. **Handler layer**
   - Write `test_handlers.py` (TDD)
   - Implement `handlers/users.py`

5. **TUI layer**
   - Implement `tui/console.py`

6. **Command layer**
   - Implement `commands/users.py`

7. **Main entry point**
   - Implement `config.py`
   - Implement `main.py`

8. **Integration tests**
   - Write `test_cli.py`

9. **Documentation**
   - Write `README.md`
   - Write `CLAUDE.md`

10. **Validation**
    - Run `make ci`
    - All tests pass
    - No lint errors
    - No type errors
