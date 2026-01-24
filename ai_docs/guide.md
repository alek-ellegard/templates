# Template Creation Guide

Instructions for creating new templates in this repository.

## Directory Structure

```
templates/
├── get-template.sh          # Template picker script
├── README.md
├── ai_docs/
│   └── guide.md             # This file
└── <category>/              # e.g., cli/, api/, lib/
    └── <template-name>/     # e.g., uv-typer-command-handler
        ├── pyproject.toml   # REQUIRED: contains placeholder name
        ├── src/
        │   └── <placeholder>/   # e.g., mycli/, myapi/
        │       └── ...
        └── tests/
            └── ...
```

## How Auto-Detection Works

The `get-template.sh` script:
1. Discovers categories from top-level directories
2. Discovers templates from subdirectories within categories
3. After download, reads `pyproject.toml` to find the placeholder name
4. Replaces all occurrences of placeholder with user's project name

**What gets renamed:**
- `src/<placeholder>/` directory → `src/<project_name>/`
- `name = "<placeholder>"` in pyproject.toml
- `<placeholder> = "<placeholder>.main:run"` entrypoint
- All `from <placeholder>` and `import <placeholder>` in .py files

## Creating a New Template

### Step 1: Choose Category and Name

```bash
# Create template directory
mkdir -p templates/api/fastapi-starter
cd templates/api/fastapi-starter
```

Categories should be broad types: `cli`, `api`, `lib`, `service`, etc.

### Step 2: Choose a Placeholder Name

Pick a short, lowercase name for your template placeholder:
- CLI templates: `mycli`
- API templates: `myapi`
- Library templates: `mylib`
- Service templates: `myservice`

Use this name consistently everywhere.

### Step 3: Create pyproject.toml

```toml
[project]
name = "myapi"                              # ← Placeholder name
version = "0.1.0"
description = "FastAPI REST API template"  # ← Shows in template picker
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
]

[project.scripts]
myapi = "myapi.main:run"                    # ← Placeholder in entrypoint
```

### Step 4: Create Source Structure

```
src/
└── myapi/                    # ← Placeholder name
    ├── __init__.py
    ├── main.py
    └── routes/
        └── __init__.py
```

### Step 5: Use Consistent Imports

```python
# In src/myapi/main.py
from myapi.routes import router    # ← Use placeholder in imports
from myapi.config import settings
```

### Step 6: Create Tests

```python
# In tests/test_main.py
from myapi.main import app         # ← Use placeholder in test imports
```

### Step 7: Add Supporting Files

```
├── Makefile           # Standard targets: install, test, lint, format
├── CLAUDE.md          # AI agent coding guidelines (optional)
├── .gitignore
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── ...
```

### Step 8: Test the Template

```bash
# From repo root, test the full flow
cd /tmp
mkdir test-project && cd test-project
git init
bash /path/to/templates/get-template.sh

# Verify renaming worked
grep -r "myapi" .  # Should find nothing
grep -r "test_project" .  # Should find renamed references
make install
make test
```

## Checklist

Before committing a new template:

- [ ] `pyproject.toml` has `name` field with placeholder
- [ ] `pyproject.toml` has `description` field (shown in picker)
- [ ] `src/<placeholder>/` directory exists
- [ ] All Python imports use the placeholder name
- [ ] `[project.scripts]` uses placeholder for both key and value
- [ ] Tests pass after renaming (`make test`)
- [ ] Makefile has standard targets: `install`, `test`, `lint`, `format`

## Example: Adding an API Template

```bash
# 1. Create structure
mkdir -p templates/api/fastapi-starter/src/myapi
mkdir -p templates/api/fastapi-starter/tests

# 2. Create pyproject.toml
cat > templates/api/fastapi-starter/pyproject.toml << 'EOF'
[project]
name = "myapi"
version = "0.1.0"
description = "FastAPI REST API with async SQLAlchemy"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.100.0", "uvicorn>=0.23.0"]

[project.scripts]
myapi = "myapi.main:run"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
EOF

# 3. Create main module
cat > templates/api/fastapi-starter/src/myapi/__init__.py << 'EOF'
__version__ = "0.1.0"
EOF

cat > templates/api/fastapi-starter/src/myapi/main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def run():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run()
EOF

# 4. Test it
cd /tmp && mkdir api-test && cd api-test && git init
bash /path/to/templates/get-template.sh
# Select api → fastapi-starter
# Enter project name or accept default
make install
make test
```

## Troubleshooting

**Template not showing in picker:**
- Ensure directory structure is `<category>/<template>/`
- Check that `pyproject.toml` exists

**Renaming not working:**
- Verify `name` field in `pyproject.toml` matches `src/<name>/` directory
- Check all imports use the placeholder name consistently

**Tests fail after renaming:**
- Search for hardcoded placeholder: `grep -r "myapi" .`
- Update any missed references
