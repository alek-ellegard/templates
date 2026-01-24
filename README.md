# Templates

A collection of project templates for quick bootstrapping.

## Quick Start

```bash
npx degit alek-ellegard/templates/cli/uv-typer-command-handler my-project
cd my-project
make install
```

## Available Templates

| Template | Path | Description |
|----------|------|-------------|
| mycli | `cli/uv-typer-command-handler` | Modern Python CLI with uv, Typer, and Rich |

## Adding New Templates

1. Create your template in a category directory (e.g., `cli/`, `api/`)
2. Add entry to `TEMPLATES` array in `get-template.sh`:
   ```bash
   "name|category/template-dir|Description"
   ```
