#!/usr/bin/env bash
set -euo pipefail

REPO="alek-ellegard/templates"

# === TEMPLATE REGISTRY ===
# Format: "name|path|description"
# Add new templates here
TEMPLATES=(
    "mycli|cli/uv-typer-command-handler|Modern Python CLI with uv, Typer, and Rich"
)
# =========================

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

# Check for degit (npx or global)
if command -v degit >/dev/null 2>&1; then
    DEGIT="degit"
elif command -v npx >/dev/null 2>&1; then
    DEGIT="npx -y degit"
else
    error "Node.js is required. Install it from https://nodejs.org"
fi

# Parse templates
declare -a NAMES=()
declare -a PATHS=()
declare -a DESCS=()

for entry in "${TEMPLATES[@]}"; do
    IFS='|' read -r name path desc <<< "$entry"
    NAMES+=("$name")
    PATHS+=("$path")
    DESCS+=("$desc")
done

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

# Download using degit
info "Downloading template '${SELECTED}'..."
$DEGIT "${REPO}/${TEMPLATE_PATH}" "$DEST"

success "Template '${SELECTED}' downloaded to '${DEST}'"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo "  cd $DEST"
echo "  make install"
echo "  make test"
