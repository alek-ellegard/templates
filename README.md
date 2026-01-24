# Templates

A collection of project templates for quick bootstrapping.

## Quick Start

Run this command to interactively select and download a template:

```bash
curl -fsSL https://raw.githubusercontent.com/alek-ellegard/templates/master/get-template.sh | bash
```

If you have `fzf` installed, you'll get fuzzy search selection. Otherwise, a numbered menu is shown.

**Requirements:** curl, tar, python3 (3.11+ or with `tomli` installed)

## Direct Download

If you know which template you want, use [degit](https://github.com/Rich-Harris/degit):

```bash
npx degit alek-ellegard/templates/cli/uv-typer-command-handler my-cli
```

## Adding New Templates

1. Create your template in a category directory (e.g., `cli/`, `api/`)
2. Ensure it has a `pyproject.toml` with `name` and `description` fields:
   ```toml
   [project]
   name = "my-template"
   description = "Short description shown in template picker"
   ```

Templates are auto-discovered from `pyproject.toml` files - no manifest needed.
