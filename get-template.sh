#!/usr/bin/env bash
set -euo pipefail

REPO="alek-ellegard/templates"
BRANCH="master"
ARCHIVE_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"

# Colors (disabled if not terminal)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' BLUE='' BOLD='' NC=''
fi

info()    { echo -e "${BLUE}→${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
error()   { echo -e "${RED}✗${NC} $1" >&2; exit 1; }

# Check dependencies
command -v curl >/dev/null 2>&1 || error "curl is required"
command -v tar >/dev/null 2>&1 || error "tar is required"
command -v python3 >/dev/null 2>&1 || error "python3 is required"

# Download and extract repo
info "Fetching templates..."

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

curl -fsSL "$ARCHIVE_URL" | tar -xz -C "$TEMP_DIR"

REPO_DIR="${TEMP_DIR}/templates-${BRANCH}"

# Discover templates by finding pyproject.toml files and extract metadata
TEMPLATES_JSON=$(python3 << 'PYTHON' "$REPO_DIR"
import sys
import json
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # fallback for Python < 3.11

repo_dir = Path(sys.argv[1])
templates = []

for pyproject in repo_dir.rglob("pyproject.toml"):
    # Skip root pyproject.toml if exists
    if pyproject.parent == repo_dir:
        continue

    try:
        data = tomllib.loads(pyproject.read_text())
        project = data.get("project", {})
        name = project.get("name", pyproject.parent.name)
        description = project.get("description", "No description")
        rel_path = str(pyproject.parent.relative_to(repo_dir))
        templates.append({
            "name": name,
            "path": rel_path,
            "description": description
        })
    except Exception:
        continue

print(json.dumps(templates))
PYTHON
)

# Parse JSON into bash arrays
declare -a NAMES=()
declare -a PATHS=()
declare -a DESCS=()

while IFS= read -r line; do
    NAMES+=("$line")
done < <(echo "$TEMPLATES_JSON" | python3 -c "import sys,json; [print(t['name']) for t in json.load(sys.stdin)]")

while IFS= read -r line; do
    PATHS+=("$line")
done < <(echo "$TEMPLATES_JSON" | python3 -c "import sys,json; [print(t['path']) for t in json.load(sys.stdin)]")

while IFS= read -r line; do
    DESCS+=("$line")
done < <(echo "$TEMPLATES_JSON" | python3 -c "import sys,json; [print(t['description']) for t in json.load(sys.stdin)]")

[[ ${#NAMES[@]} -eq 0 ]] && error "No templates found"

# Select template
select_with_fzf() {
    local selection
    selection=$(for i in "${!NAMES[@]}"; do
        echo -e "${NAMES[$i]}\t${DESCS[$i]}"
    done | fzf --header="Select a template:" --with-nth=1,2 --delimiter='\t' --height=~50% --reverse)
    echo "${selection%%$'\t'*}"
}

select_with_menu() {
    echo ""
    echo -e "${BOLD}Available templates:${NC}"
    echo ""
    for i in "${!NAMES[@]}"; do
        echo -e "  ${BOLD}$((i+1)))${NC} ${NAMES[$i]}"
        echo -e "     ${DESCS[$i]}"
        echo ""
    done

    local choice
    while true; do
        read -rp "Select template [1-${#NAMES[@]}]: " choice
        if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#NAMES[@]} )); then
            echo "${NAMES[$((choice-1))]}"
            return
        fi
        echo "Invalid selection. Please enter a number between 1 and ${#NAMES[@]}."
    done
}

# Use fzf if available and interactive, otherwise fall back to menu
if [[ -t 0 ]] && command -v fzf >/dev/null 2>&1; then
    SELECTED=$(select_with_fzf)
else
    SELECTED=$(select_with_menu)
fi

[[ -z "$SELECTED" ]] && error "No template selected"

# Find the path for selected template
TEMPLATE_PATH=""
for i in "${!NAMES[@]}"; do
    if [[ "${NAMES[$i]}" == "$SELECTED" ]]; then
        TEMPLATE_PATH="${PATHS[$i]}"
        break
    fi
done

[[ -z "$TEMPLATE_PATH" ]] && error "Template path not found"

# Ask for destination directory
DEFAULT_DEST="${SELECTED}"
if [[ -t 0 ]]; then
    read -rp "Destination directory [${DEFAULT_DEST}]: " DEST
    DEST="${DEST:-$DEFAULT_DEST}"
else
    DEST="$DEFAULT_DEST"
fi

# Check if destination exists
[[ -e "$DEST" ]] && error "Destination '$DEST' already exists"

# Move template to destination
mv "${REPO_DIR}/${TEMPLATE_PATH}" "$DEST"

success "Template '${SELECTED}' downloaded to '${DEST}'"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo "  cd $DEST"
echo "  make install"
echo "  make test"
