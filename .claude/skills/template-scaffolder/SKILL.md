---
name: template-scaffolder
description: Create new project templates with proper structure. Use when user says "create template", "add template", "scaffold template", or "new template for X".
---

# Purpose

Provide knowledge for creating new project templates in this repository. Templates are scaffolds that users download and rename to bootstrap new projects.

## Variables

CATEGORY: Template category (cli, api, lib, service)
TEMPLATE_NAME: Template directory name in kebab-case (e.g., fastapi-starter)
PLACEHOLDER: Python package name used in template (e.g., myapi) - lowercase, underscores

## Instructions

**ALWAYS**:
- Create templates in `<category>/<template-name>/` structure
- Use a consistent placeholder name throughout (pyproject.toml, src/, imports)
- Include pyproject.toml with `name` and `description` fields
- Include Makefile with standard targets: install, test, lint, format
- Include tests/ directory with working tests
- Verify template works after creation (make install && make test)

**NEVER**:
- Modify existing templates (only create new ones)
- Skip placeholder setup - the renaming system depends on it
- Create templates outside category directories
- Use inconsistent placeholder names across files
- Create templates without pyproject.toml (breaks auto-detection)

## Workflow

### 1. Gather Requirements

Ask user for:
1. **Category**: What type of project? (cli, api, lib, service)
2. **Template name**: Descriptive kebab-case name (e.g., fastapi-starter)
3. **Placeholder**: Package name to use (default: myapi for api, mycli for cli, etc.)
4. **Description**: One-line description for pyproject.toml

### 2. Create Directory Structure

```bash
mkdir -p templates/<category>/<template-name>/src/<placeholder>
mkdir -p templates/<category>/<template-name>/tests/unit
mkdir -p templates/<category>/<template-name>/tests/integration
```

### 3. Create pyproject.toml

```toml
[project]
name = "<placeholder>"                    # Auto-detected by get-template.sh
version = "0.1.0"
description = "<description>"             # Shown in template picker
requires-python = ">=3.12"
dependencies = [
    # Add dependencies here
]

[project.scripts]
<placeholder> = "<placeholder>.main:run"  # Entrypoint

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "ruff>=0.4.0",
]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 4. Create Source Files

**src/<placeholder>/__init__.py**:
```python
__version__ = "0.1.0"
```

**src/<placeholder>/main.py**:
```python
def run() -> None:
    """Entry point."""
    print("Hello from <placeholder>")

if __name__ == "__main__":
    run()
```

### 5. Create Makefile

```makefile
.PHONY: install format lint test ci clean

install:
	uv sync

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

test:
	uv run pytest tests -v

ci: install lint test

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

### 6. Create Tests

**tests/__init__.py**: empty

**tests/conftest.py**:
```python
import pytest
```

**tests/unit/__init__.py**: empty

**tests/unit/test_main.py**:
```python
from <placeholder>.main import run

def test_run(capsys):
    run()
    captured = capsys.readouterr()
    assert "Hello" in captured.out
```

### 7. Create Supporting Files

**.gitignore**:
```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
*.egg-info/
dist/
build/
```

**CLAUDE.md** (optional): AI agent coding guidelines

### 8. Verify Template

```bash
cd templates/<category>/<template-name>
make install
make test
```

### 9. Test Full Flow

```bash
cd /tmp
mkdir test-project && cd test-project
git init
bash /path/to/templates/get-template.sh
# Select your new template
# Verify renaming worked
grep -r "<placeholder>" .  # Should find nothing after rename
make install && make test
```

## Cookbook

<If: User wants CLI template>
<Then: Use `mycli` as placeholder, include typer and rich dependencies, add commands/ and handlers/ structure>

<If: User wants API template>
<Then: Use `myapi` as placeholder, include fastapi and uvicorn, add routes/ structure>

<If: User wants library template>
<Then: Use `mylib` as placeholder, minimal dependencies, focus on src/ and tests/>

<If: Template needs database>
<Then: Add sqlalchemy to dependencies, create models/ and repository/ directories>

<If: Placeholder appears in test output after rename>
<Then: Search for hardcoded strings: `grep -r "<placeholder>" .` and update>

## Reference

### How Templates Are Consumed

When users download a template via `get-template.sh`:
1. Script reads `name` from pyproject.toml to find placeholder
2. Renames `src/<placeholder>/` to `src/<project_name>/`
3. Updates pyproject.toml name and entrypoint
4. Updates all Python imports

**This means:** Your template's placeholder name MUST be consistent across all files for renaming to work correctly.

Full guide: [ai_docs/guide.md](../../ai_docs/guide.md)
