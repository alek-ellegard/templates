# CLAUDE.md - CLI Command Handler Architecture

## Architecture

```
commands/ → handlers/ → repository/
    ↓           ↓            ↓
   tui/      domain/      (JSON)
```

Commands are thin. Handlers contain logic. Repository handles persistence.

## Design Principles

### Tracer Bullet Implementation

- New feature = vertical slice through ALL layers
- Start with test (TDD)
- Then: model → repository → handler → command → tui
- Simple first, enhance later

### Native Python Only

```python
# YES - plain class
class Item:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

# NO - dataclass, pydantic, attrs

# YES - factory function
def item_from_dict(data: dict[str, str]) -> Item:
    return Item(id=data["id"], name=data["name"])

# NO - classmethod constructors
```

### Explicit Types

```python
# YES
def get(self, id: str) -> Item | None:

# NO
def get(self, id: str) -> Optional[Item]:

# YES - StrEnum for fixed values
class Status(StrEnum):
    ACTIVE = "active"

# NO - plain strings for fixed values
```

### TDD Workflow

1. Write failing test
2. Implement minimum code to pass
3. Refactor
4. Repeat

## Error Handling

Exceptions bubble up: repository → handler → command → main.

```python
# In handler
if item is None:
    raise ItemNotFoundError(f"Item {id} not found")

# In main.py
except CLIError as e:
    tui.error(e.message)
    raise typer.Exit(e.exit_code)
```

## Adding a New Feature

Vertical slice through all layers:

1. **Test first** (`tests/unit/test_handlers.py`)
2. **Domain** (`domain/models.py`) — add models/enums if needed
3. **Repository protocol** (`repository/base.py`) — add method signature
4. **Repository impl** (`repository/json.py`) — implement persistence
5. **Handler** (`handlers/{resource}.py`) — business logic
6. **Command** (`commands/{resource}.py`) — thin CLI entry point
7. **Integration test** (`tests/integration/test_cli.py`)

## File Naming

| Layer | Naming |
|-------|--------|
| Commands | `commands/{resource}.py` |
| Handlers | `handlers/{resource}.py` |
| Repository | `repository/{implementation}.py` |
| Domain | `domain/models.py` |
| TUI | `tui/console.py` |

## Testing

- Unit tests: test handlers with in-memory repository
- Integration tests: test CLI with CliRunner and temp files
- No mocking of domain models
