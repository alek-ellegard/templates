#!/usr/bin/env bash
# Validate template scaffolding artifacts exist
# Exit 0: validation passed, Exit 2: validation failed (blocks stop)

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Find template directories (category/template-name pattern)
# Look for directories that contain pyproject.toml (indicates a template)
find_templates() {
    find "$PROJECT_DIR" -maxdepth 3 -name "pyproject.toml" -type f 2>/dev/null | while read -r pyproject; do
        template_dir=$(dirname "$pyproject")
        # Skip if it's the root or .claude directory
        [[ "$template_dir" == "$PROJECT_DIR" ]] && continue
        [[ "$template_dir" == *".claude"* ]] && continue
        # Check if it matches category/template pattern (2 levels deep)
        rel_path="${template_dir#$PROJECT_DIR/}"
        if [[ "$rel_path" =~ ^[^/]+/[^/]+$ ]]; then
            echo "$template_dir"
        fi
    done
}

validate_template() {
    local template_dir="$1"
    local failed=0
    local output=""

    # Check files and dirs with status markers
    check() {
        local type="$1" path="$2" label="$3"
        if [[ "$type" == "f" && -f "$template_dir/$path" ]] || \
           [[ "$type" == "d" && -d "$template_dir/$path" ]]; then
            output+="✓ $label\n"
        else
            output+="✗ $label\n"
            failed=1
        fi
    }

    check f "pyproject.toml" "pyproject.toml"
    check f "Makefile" "Makefile"
    check f ".gitignore" ".gitignore"
    check d "src" "src/"
    check d "tests" "tests/"

    # Check pyproject.toml fields
    if [[ -f "$template_dir/pyproject.toml" ]]; then
        if grep -q '^\s*name\s*=' "$template_dir/pyproject.toml"; then
            output+="✓ pyproject.name\n"
        else
            output+="✗ pyproject.name\n"
            failed=1
        fi
        if grep -q '^\s*description\s*=' "$template_dir/pyproject.toml"; then
            output+="✓ pyproject.description\n"
        else
            output+="✗ pyproject.description\n"
            failed=1
        fi
    fi

    # Check src/ has package
    if [[ -d "$template_dir/src" ]]; then
        local pkg_count
        pkg_count=$(find "$template_dir/src" -maxdepth 1 -type d ! -name "src" | wc -l)
        if [[ "$pkg_count" -gt 0 ]]; then
            output+="✓ src/<pkg>/\n"
        else
            output+="✗ src/<pkg>/\n"
            failed=1
        fi
    fi

    # Check tests/ has test files
    if [[ -d "$template_dir/tests" ]]; then
        local test_count
        test_count=$(find "$template_dir/tests" -name "test_*.py" 2>/dev/null | wc -l)
        if [[ "$test_count" -gt 0 ]]; then
            output+="✓ test_*.py\n"
        else
            output+="✗ test_*.py\n"
            failed=1
        fi
    fi

    if [[ "$failed" -eq 1 ]]; then
        echo "${template_dir#$PROJECT_DIR/}:" >&2
        echo -e "$output" >&2
        return 1
    fi

    return 0
}

main() {
    local templates
    templates=$(find_templates)

    if [[ -z "$templates" ]]; then
        # No templates found - might be early in scaffolding
        echo "No template directories found yet"
        exit 0
    fi

    local failed=0
    while IFS= read -r template_dir; do
        if ! validate_template "$template_dir"; then
            failed=1
        fi
    done <<< "$templates"

    if [[ "$failed" -eq 1 ]]; then
        exit 2
    fi
    exit 0
}

main
