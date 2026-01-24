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

# Check for degit
if command -v degit >/dev/null 2>&1; then
    DEGIT="degit"
elif command -v npx >/dev/null 2>&1; then
    DEGIT="npx -y degit"
else
    error "Node.js is required. Install it from https://nodejs.org"
fi

command -v python3 >/dev/null 2>&1 || error "python3 is required"

# Use jsDelivr API to list repo contents (different CDN than raw.githubusercontent.com)
JSDELIVR_API="https://data.jsdelivr.com/v1/package/gh/${REPO}@master"

info "Fetching template categories..."

REPO_DATA=$(curl -fsSL --connect-timeout 10 "$JSDELIVR_API") || error "Failed to fetch repo listing"

# Extract top-level directories (categories like cli/, api/, etc.)
CATEGORIES=$(echo "$REPO_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
files = data.get('files', [])
# Get top-level directories, exclude hidden and files
dirs = [f['name'] for f in files if f['type'] == 'directory' and not f['name'].startswith('.')]
for d in sorted(dirs):
    print(d)
")

[[ -z "$CATEGORIES" ]] && error "No template categories found"

# Select category
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

# Convert to array
readarray -t CAT_ARRAY <<< "$CATEGORIES"

SELECTED_CAT=$(select_item "Select category:" "${CAT_ARRAY[@]}")
[[ -z "$SELECTED_CAT" ]] && error "No category selected"

# Fetch templates in selected category
info "Fetching templates in ${SELECTED_CAT}/..."

CAT_DATA=$(curl -fsSL --connect-timeout 10 "${JSDELIVR_API}/flat") || error "Failed to fetch category listing"

# Extract subdirectories of selected category
TEMPLATES=$(echo "$CAT_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
files = data.get('files', [])
category = '${SELECTED_CAT}'
# Find directories inside the category
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
")

[[ -z "$TEMPLATES" ]] && error "No templates found in ${SELECTED_CAT}/"

readarray -t TMPL_ARRAY <<< "$TEMPLATES"

SELECTED_TMPL=$(select_item "Select template:" "${TMPL_ARRAY[@]}")
[[ -z "$SELECTED_TMPL" ]] && error "No template selected"

TEMPLATE_PATH="${SELECTED_CAT}/${SELECTED_TMPL}"

# Ask for destination directory
DEFAULT_DEST="${SELECTED_TMPL}"
if [[ -t 0 ]]; then
    read -rp "Destination directory [${DEFAULT_DEST}]: " DEST
    DEST="${DEST:-$DEFAULT_DEST}"
else
    DEST="$DEFAULT_DEST"
fi

# Download using degit
info "Downloading ${TEMPLATE_PATH}..."
$DEGIT "${REPO}/${TEMPLATE_PATH}" "$DEST"

success "Template downloaded to '${DEST}'"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo "  cd $DEST"
echo "  make install"
echo "  make test"
