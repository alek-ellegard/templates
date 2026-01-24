# CLAUDE.md - AI Agent Coding Guidelines

read @AGENTS.md for project management

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

## Documentation

For comprehensive codebase architecture, data flow diagrams, and navigation guides, see `docs/CODEBASE_MAP.md`.
