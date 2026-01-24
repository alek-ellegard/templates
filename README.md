# Templates

Project templates for quick bootstrapping with automatic renaming.

## Quick Start

`nvim ~/.zshrc`
-> add `alias templates="bash <(curl -fsSL 'https://cdn.jsdelivr.net/gh/alek-ellegard/templates@master/get-template.sh')"`

**Interactive mode:**

```bash
mkdir my-project && cd my-project
git init
bash <(curl -fsSL "https://cdn.jsdelivr.net/gh/alek-ellegard/templates@master/get-template.sh")
```

**Non-interactive mode (for agents/scripts):**

```bash
./get-template.sh -c cli -t uv-typer-command-handler -n my_project
```

**List available templates:**

```bash
./get-template.sh --list
```

## Options

| Option | Description |
|--------|-------------|
| `-c, --category` | Template category (cli, api, lib, etc.) |
| `-t, --template` | Template name within category |
| `-d, --dest` | Destination directory (default: current dir) |
| `-n, --name` | Project name for renaming (default: directory name) |
| `-l, --list` | List available templates and exit |
| `-h, --help` | Show help message |

## Direct Download (without renaming)

```bash
npx degit alek-ellegard/templates/cli/uv-typer-command-handler my-project
```

## Creating New Templates

claude 'use skill template-scaffolder - create new cli template for ..'

See [ai_docs/guide.md](ai_docs/guide.md) for detailed instructions.

**Quick summary:**

1. Create `<category>/<template-name>/` directory
2. Use a placeholder name (e.g., `myapi`) consistently in:
   - `src/<placeholder>/` directory
   - `pyproject.toml` name field
   - All Python imports
3. The script auto-detects the placeholder from `pyproject.toml`
