---
last_mapped: 2026-01-24T00:00:00Z
total_files: 36
total_tokens: 20517
---

# Codebase Map

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Input                           │
│                    mycli users <cmd> [args]                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  main.py                                                    │
│  - Typer app with callback for DI                           │
│  - Initializes AppContext (config, repo, handler, tui)      │
│  - Global CLIError exception handler                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  commands/users.py                                          │
│  - Thin CLI layer: parse args, call handler, display via TUI│
│  - get_handler(ctx), get_tui(ctx) helpers                   │
│  - Commands: create, list, get, delete                      │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
┌────────────▼────────────┐    ┌──────────────▼───────────────┐
│  handlers/users.py      │    │  tui/console.py              │
│  - Business logic       │    │  - Rich console output       │
│  - Validation           │    │  - Tables, colors, prompts   │
│  - Exception mapping    │    │  - success/error/info        │
└────────────┬────────────┘    └──────────────────────────────┘
             │
┌────────────▼────────────┐
│  repository/json.py     │
│  - JSON file persistence│
│  - In-memory cache      │
│  - Auto-save on mutate  │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  domain/models.py       │
│  - User, UserStatus     │
│  - Factory functions    │
│  - Serialization        │
└─────────────────────────┘
```

## Directory Structure

```
uv-typer-command-handler/
├── pyproject.toml          # Project config, dependencies, entry point
├── Makefile                # Dev workflow (install, lint, test, ci)
├── CLAUDE.md               # AI coding guidelines
├── AGENTS.md               # Issue tracking with beads
│
├── src/mycli/
│   ├── __init__.py
│   ├── main.py             # Entry point, DI wiring, error handling
│   ├── config.py           # AppConfig, AppContext classes
│   ├── exceptions.py       # ExitCode enum, CLIError hierarchy
│   │
│   ├── domain/
│   │   ├── __init__.py     # Exports: User, UserStatus, factories
│   │   └── models.py       # User class, StrEnum, factory functions
│   │
│   ├── repository/
│   │   ├── __init__.py     # Exports: UserRepository, JsonUserRepository
│   │   ├── base.py         # UserRepository Protocol
│   │   └── json.py         # JSON file implementation
│   │
│   ├── handlers/
│   │   ├── __init__.py     # Exports: UserHandler
│   │   └── users.py        # Business logic (create, get, list, delete)
│   │
│   ├── commands/
│   │   ├── __init__.py     # Exports: users_app
│   │   └── users.py        # CLI commands (thin, delegates to handler)
│   │
│   └── tui/
│       ├── __init__.py     # Exports: TUI
│       └── console.py      # Rich console wrapper
│
├── tests/
│   ├── conftest.py         # Fixtures: InMemoryUserRepository, runner
│   ├── unit/
│   │   ├── test_models.py          # Domain model tests
│   │   ├── test_handlers.py        # Handler logic tests
│   │   ├── test_repository.py      # JSON persistence tests
│   │   ├── test_repository_protocol.py  # Protocol compliance tests
│   │   ├── test_inmemory_repo.py   # Test double validation
│   │   ├── test_exceptions.py      # Exception hierarchy tests
│   │   └── test_tui.py             # TUI output tests
│   └── integration/
│       └── test_cli.py             # End-to-end CLI tests
│
└── specs/
    └── cli-template-prd.md         # Full PRD with design principles
```

## Module Guide

### src/mycli/ (Root)

| File | Purpose | Key Exports |
|------|---------|-------------|
| main.py | Entry point with DI | `app`, `run()` |
| config.py | Configuration classes | `AppConfig`, `AppContext` |
| exceptions.py | Exception hierarchy | `ExitCode`, `CLIError`, `UserNotFoundError`, `UserExistsError`, `RepositoryError` |

**Dependencies**: typer, pathlib, all internal modules

### src/mycli/domain/

| File | Purpose | Key Exports |
|------|---------|-------------|
| models.py | User entity, status enum | `User`, `UserStatus`, `create_user()`, `user_from_dict()` |

**Dependencies**: uuid, enum.StrEnum (no external deps)

**Patterns**:
- Native Python classes (no dataclasses)
- Factory functions instead of classmethods
- StrEnum for type-safe status

### src/mycli/repository/

| File | Purpose | Key Exports |
|------|---------|-------------|
| base.py | Repository protocol | `UserRepository` (Protocol) |
| json.py | JSON implementation | `JsonUserRepository` |

**Dependencies**: json, pathlib, domain models

**Patterns**:
- Protocol with @runtime_checkable
- In-memory cache with auto-save
- RepositoryError wraps I/O errors

### src/mycli/handlers/

| File | Purpose | Key Exports |
|------|---------|-------------|
| users.py | Business logic | `UserHandler` |

**Dependencies**: domain models, repository protocol, exceptions

**Patterns**:
- Constructor injection of repository
- Converts None returns to exceptions
- Validates before persistence

### src/mycli/commands/

| File | Purpose | Key Exports |
|------|---------|-------------|
| users.py | CLI commands | `app`, `create`, `list`, `get`, `delete` |

**Dependencies**: typer, handlers, tui, exceptions

**Patterns**:
- Thin commands (delegate to handler)
- Context helpers: `get_handler()`, `get_tui()`
- Confirmation prompts for destructive ops

### src/mycli/tui/

| File | Purpose | Key Exports |
|------|---------|-------------|
| console.py | Rich output | `TUI` |

**Dependencies**: rich (Console, Table)

**Patterns**:
- Separate stderr console for errors
- Semantic methods: success/error/info
- Domain-aware formatting

## Data Flow

### Create User Flow

```
1. User runs: mycli users create user@example.com
                    │
2. main.py callback │
   ├── Creates AppConfig(data_dir)
   ├── Creates JsonUserRepository(users_file)
   ├── Creates UserHandler(repository)
   ├── Creates TUI()
   └── Stores in ctx.obj as dict
                    │
3. commands/users.py create()
   ├── get_handler(ctx) → UserHandler
   ├── get_tui(ctx) → TUI
   └── handler.create(email)
                    │
4. handlers/users.py create()
   ├── repository.get_by_email(email) → None (no duplicate)
   ├── create_user(email) → User with UUID
   └── repository.add(user) → persists to JSON
                    │
5. commands/users.py (continued)
   ├── tui.success("Created user {id}")
   └── tui.user_detail(user) → Rich formatted output
```

### Error Flow

```
1. UserNotFoundError raised in handler
                    │
2. Bubbles to command layer
   └── CLIError caught in commands/users.py
       ├── tui.error(e.message)
       └── raise typer.Exit(e.exit_code)
                    │
3. OR bubbles to main.py run()
   └── CLIError caught globally
       ├── tui.error(e.message)
       └── raise typer.Exit(e.exit_code)
```

## Conventions

### Code Style

| Convention | Example |
|------------|---------|
| Type unions | `User \| None` (not `Optional[User]`) |
| Enums | `StrEnum` for strings, `IntEnum` for codes |
| Classes | Native `__init__`, no decorators |
| Factories | Module-level functions, not classmethods |
| Exports | Explicit `__all__` in `__init__.py` |

### Error Handling

| Layer | Raises | Catches |
|-------|--------|---------|
| Repository | `RepositoryError` | JSON/IO errors |
| Handler | `UserNotFoundError`, `UserExistsError` | - |
| Command | - | `CLIError` |
| main.py | - | `CLIError` (global) |

### Testing

| Type | Location | Strategy |
|------|----------|----------|
| Unit | tests/unit/ | InMemoryUserRepository fixture |
| Integration | tests/integration/ | CliRunner + tmp_data_dir |
| Protocol | test_repository_protocol.py | isinstance checks |

## Gotchas

### Context Storage
- `ctx.obj` is a **dict** (not AppContext object) due to Typer serialization
- Access via `ctx.obj["user_handler"]`, not `ctx.obj.user_handler`

### Auto-Save Behavior
- `JsonUserRepository.add()` and `delete()` call `save()` automatically
- No need for explicit save, but also no batch operations

### Email Uniqueness
- `handler.create()` checks email uniqueness before creating
- Race condition possible with concurrent access (no locking)

### Default Data Directory
- Without `--data-dir`, uses `~/.mycli/users.json`
- Parent directories created automatically on first save

### Test Double Validation
- `InMemoryUserRepository` is itself tested in `test_inmemory_repo.py`
- Ensures test double matches real implementation behavior

## Navigation Guide

**To add a new command**:
1. Write test in `tests/unit/test_handlers.py`
2. Add method to `handlers/users.py`
3. Add command to `commands/users.py`
4. Write integration test in `tests/integration/test_cli.py`

**To add a new entity**:
1. Create model in `domain/models.py`
2. Define protocol in `repository/base.py`
3. Implement in `repository/json.py`
4. Create handler in `handlers/{entity}.py`
5. Add commands in `commands/{entity}.py`
6. Wire up in `main.py`

**To run quality checks**:
```bash
make ci          # Full pipeline: install, lint, typecheck, test
make test        # Just tests
make format      # Auto-fix lint issues
```

**To test manually**:
```bash
uv run mycli users create test@example.com
uv run mycli users list
uv run mycli users get <uuid>
uv run mycli users delete <uuid> --force
```
