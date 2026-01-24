#!/usr/bin/env bash
set -euo pipefail

REPO="alek-ellegard/templates"

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

usage() {
    cat << EOF
Usage: get-template.sh [OPTIONS]

Download and scaffold a project template.

Options:
  -c, --category NAME    Template category (cli, api, lib, etc.)
  -t, --template NAME    Template name within category
  -d, --dest PATH        Destination directory (default: current dir)
  -n, --name NAME        Project name for renaming (default: directory name)
  -l, --list             List available templates and exit
  -h, --help             Show this help message

Interactive mode (no arguments):
  ./get-template.sh

Non-interactive mode (for agents):
  ./get-template.sh -c cli -t uv-typer-command-handler -n my_project

Examples:
  ./get-template.sh --list
  ./get-template.sh -c cli -t uv-typer-command-handler
  ./get-template.sh --category api --template fastapi-starter --name myapi
EOF
    exit 0
}

# Parse arguments
ARG_CATEGORY=""
ARG_TEMPLATE=""
ARG_DEST=""
ARG_NAME=""
ARG_LIST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--category) ARG_CATEGORY="$2"; shift 2 ;;
        -t|--template) ARG_TEMPLATE="$2"; shift 2 ;;
        -d|--dest)     ARG_DEST="$2"; shift 2 ;;
        -n|--name)     ARG_NAME="$2"; shift 2 ;;
        -l|--list)     ARG_LIST=true; shift ;;
        -h|--help)     usage ;;
        *)             error "Unknown option: $1. Use --help for usage." ;;
    esac
done

# Check for degit
if command -v degit >/dev/null 2>&1; then
    DEGIT="degit"
elif command -v npx >/dev/null 2>&1; then
    DEGIT="npx -y degit"
else
    error "Node.js is required. Install it from https://nodejs.org"
fi

command -v python3 >/dev/null 2>&1 || error "python3 is required"

# Use jsDelivr API to list repo contents
JSDELIVR_API="https://data.jsdelivr.com/v1/package/gh/${REPO}@master"

info "Fetching template categories..."

REPO_DATA=$(curl -fsSL --connect-timeout 10 "$JSDELIVR_API") || error "Failed to fetch repo listing"

# Extract top-level directories (categories)
CATEGORIES=$(echo "$REPO_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
files = data.get('files', [])
dirs = [f['name'] for f in files if f['type'] == 'directory' and not f['name'].startswith('.')]
for d in sorted(dirs):
    print(d)
")

[[ -z "$CATEGORIES" ]] && error "No template categories found"

# Fetch flat listing for template discovery
CAT_DATA=$(curl -fsSL --connect-timeout 10 "${JSDELIVR_API}/flat") || error "Failed to fetch template listing"

# Function to get templates in a category
get_templates_in_category() {
    local category="$1"
    echo "$CAT_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
files = data.get('files', [])
category = '${category}'
seen = set()
for f in files:
    path = f['name'].lstrip('/')
    if path.startswith(category + '/'):
        rest = path[len(category)+1:]
        if '/' in rest:
            subdir = rest.split('/')[0]
            if subdir not in seen:
                seen.add(subdir)
                print(subdir)
"
}

# Handle --list flag
if [[ "$ARG_LIST" == true ]]; then
    echo ""
    echo -e "${BOLD}Available templates:${NC}"
    echo ""
    for cat in $CATEGORIES; do
        templates=$(get_templates_in_category "$cat")
        if [[ -n "$templates" ]]; then
            echo -e "${BOLD}${cat}/${NC}"
            while IFS= read -r tmpl; do
                echo "  - ${tmpl}"
            done <<< "$templates"
            echo ""
        fi
    done
    exit 0
fi

# Interactive selection function
select_item() {
    local prompt="$1"
    shift
    local items=("$@")

    if [[ -t 0 ]] && command -v fzf >/dev/null 2>&1; then
        printf '%s\n' "${items[@]}" | fzf --header="$prompt" --height=~50% --reverse
    else
        echo "" >&2
        echo -e "${BOLD}${prompt}${NC}" >&2
        echo "" >&2
        for i in "${!items[@]}"; do
            echo -e "  ${BOLD}$((i+1)))${NC} ${items[$i]}" >&2
        done
        echo "" >&2

        local choice
        while true; do
            read -rp "Select [1-${#items[@]}]: " choice
            if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#items[@]} )); then
                echo "${items[$((choice-1))]}"
                return
            fi
            echo "Invalid selection." >&2
        done
    fi
}

# Determine category (from arg or interactive)
if [[ -n "$ARG_CATEGORY" ]]; then
    SELECTED_CAT="$ARG_CATEGORY"
    # Validate category exists
    if ! echo "$CATEGORIES" | grep -qx "$SELECTED_CAT"; then
        error "Category '$SELECTED_CAT' not found. Available: $(echo $CATEGORIES | tr '\n' ' ')"
    fi
else
    readarray -t CAT_ARRAY <<< "$CATEGORIES"
    SELECTED_CAT=$(select_item "Select category:" "${CAT_ARRAY[@]}")
    [[ -z "$SELECTED_CAT" ]] && error "No category selected"
fi

# Get templates in selected category
info "Fetching templates in ${SELECTED_CAT}/..."
TEMPLATES=$(get_templates_in_category "$SELECTED_CAT")
[[ -z "$TEMPLATES" ]] && error "No templates found in ${SELECTED_CAT}/"

# Determine template (from arg or interactive)
if [[ -n "$ARG_TEMPLATE" ]]; then
    SELECTED_TMPL="$ARG_TEMPLATE"
    # Validate template exists
    if ! echo "$TEMPLATES" | grep -qx "$SELECTED_TMPL"; then
        error "Template '$SELECTED_TMPL' not found in ${SELECTED_CAT}/. Available: $(echo $TEMPLATES | tr '\n' ' ')"
    fi
else
    readarray -t TMPL_ARRAY <<< "$TEMPLATES"
    SELECTED_TMPL=$(select_item "Select template:" "${TMPL_ARRAY[@]}")
    [[ -z "$SELECTED_TMPL" ]] && error "No template selected"
fi

TEMPLATE_PATH="${SELECTED_CAT}/${SELECTED_TMPL}"

# Determine destination (from arg or interactive)
if [[ -n "$ARG_DEST" ]]; then
    DEST="$ARG_DEST"
elif [[ -t 0 ]]; then
    read -rp "Destination [. = current dir]: " DEST
    DEST="${DEST:-.}"
else
    DEST="."
fi

# Download using degit
info "Downloading ${TEMPLATE_PATH}..."
$DEGIT "${REPO}/${TEMPLATE_PATH}" "$DEST" --force

# Determine working directory for renaming
if [[ "$DEST" == "." ]]; then
    WORK_DIR="$(pwd)"
else
    WORK_DIR="$DEST"
fi

# Auto-detect template placeholder name from pyproject.toml
if [[ -f "${WORK_DIR}/pyproject.toml" ]]; then
    TEMPLATE_NAME=$(python3 -c "
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib
with open('${WORK_DIR}/pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
print(data.get('project', {}).get('name', 'mycli'))
" 2>/dev/null) || TEMPLATE_NAME="mycli"
else
    TEMPLATE_NAME="mycli"
fi

# Determine project name (from arg or interactive)
DEFAULT_NAME=$(basename "$(cd "$WORK_DIR" && pwd)")
DEFAULT_NAME=$(echo "$DEFAULT_NAME" | tr '[:upper:]' '[:lower:]' | tr '-' '_' | tr ' ' '_')

if [[ -n "$ARG_NAME" ]]; then
    PROJECT_NAME="$ARG_NAME"
elif [[ -t 0 ]]; then
    read -rp "Project name [${DEFAULT_NAME}]: " PROJECT_NAME
    PROJECT_NAME="${PROJECT_NAME:-$DEFAULT_NAME}"
else
    PROJECT_NAME="$DEFAULT_NAME"
fi

# Sanitize project name
PROJECT_NAME=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr '-' '_' | tr ' ' '_')

# Rename if different from template default
if [[ "$PROJECT_NAME" != "$TEMPLATE_NAME" ]]; then
    info "Renaming ${TEMPLATE_NAME} → ${PROJECT_NAME}..."

    # Rename src directory
    if [[ -d "${WORK_DIR}/src/${TEMPLATE_NAME}" ]]; then
        mv "${WORK_DIR}/src/${TEMPLATE_NAME}" "${WORK_DIR}/src/${PROJECT_NAME}"
    fi

    # Update pyproject.toml
    if [[ -f "${WORK_DIR}/pyproject.toml" ]]; then
        sed -i.bak "s/name = \"${TEMPLATE_NAME}\"/name = \"${PROJECT_NAME}\"/g" "${WORK_DIR}/pyproject.toml"
        sed -i.bak "s/${TEMPLATE_NAME} = \"${TEMPLATE_NAME}/${PROJECT_NAME} = \"${PROJECT_NAME}/g" "${WORK_DIR}/pyproject.toml"
        rm -f "${WORK_DIR}/pyproject.toml.bak"
    fi

    # Update Python imports in all .py files
    find "${WORK_DIR}" -name "*.py" -type f -exec sed -i.bak "s/from ${TEMPLATE_NAME}/from ${PROJECT_NAME}/g; s/import ${TEMPLATE_NAME}/import ${PROJECT_NAME}/g" {} \;
    find "${WORK_DIR}" -name "*.py.bak" -type f -delete
fi

if [[ "$DEST" == "." ]]; then
    success "Template '${PROJECT_NAME}' ready in current directory"
else
    success "Template '${PROJECT_NAME}' ready in '${DEST}'"
fi

echo ""
echo -e "${BOLD}Next steps:${NC}"
if [[ "$DEST" != "." ]]; then
    echo "  cd $DEST"
fi
echo "  make install"
echo "  make test"
echo "  ${PROJECT_NAME} --help"
