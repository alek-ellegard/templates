# Templates

Project templates for quick bootstrapping with automatic renaming.

## Quick Start

```bash
mkdir my-project && cd my-project
git init
bash <(curl -fsSL "https://cdn.jsdelivr.net/gh/alek-ellegard/templates@master/get-template.sh")
```

The script will:
1. Show available categories (cli, api, etc.)
2. Show templates in selected category
3. Download to current directory
4. Prompt for project name (default: directory name)
5. Rename all references from template placeholder to your project name

## Direct Download (without renaming)

```bash
npx degit alek-ellegard/templates/cli/uv-typer-command-handler my-project
```

## Creating New Templates

See [ai_docs/guide.md](ai_docs/guide.md) for detailed instructions.

**Quick summary:**
1. Create `<category>/<template-name>/` directory
2. Use a placeholder name (e.g., `myapi`) consistently in:
   - `src/<placeholder>/` directory
   - `pyproject.toml` name field
   - All Python imports
3. The script auto-detects the placeholder from `pyproject.toml`
