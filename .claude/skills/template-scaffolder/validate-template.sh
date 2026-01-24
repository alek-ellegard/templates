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
    local errors=()

    # Required files
    local required_files=(
        "pyproject.toml"
        "Makefile"
        ".gitignore"
    )

    # Required directories
    local required_dirs=(
        "src"
        "tests"
    )

    # Check required files
    for file in "${required_files[@]}"; do
        if [[ ! -f "$template_dir/$file" ]]; then
            errors+=("Missing file: $file")
        fi
    done

    # Check required directories
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$template_dir/$dir" ]]; then
            errors+=("Missing directory: $dir/")
        fi
    done

    # Validate pyproject.toml has required fields
    if [[ -f "$template_dir/pyproject.toml" ]]; then
        if ! grep -q '^\s*name\s*=' "$template_dir/pyproject.toml"; then
            errors+=("pyproject.toml missing 'name' field")
        fi
        if ! grep -q '^\s*description\s*=' "$template_dir/pyproject.toml"; then
            errors+=("pyproject.toml missing 'description' field")
        fi
    fi

    # Check src/ has a package directory
    if [[ -d "$template_dir/src" ]]; then
        local pkg_count
        pkg_count=$(find "$template_dir/src" -maxdepth 1 -type d ! -name "src" | wc -l)
        if [[ "$pkg_count" -eq 0 ]]; then
            errors+=("src/ has no package directory (e.g., src/myapi/)")
        fi
    fi

    # Check tests/ has at least one test file or subdirectory
    if [[ -d "$template_dir/tests" ]]; then
        local test_files
        test_files=$(find "$template_dir/tests" -name "test_*.py" -o -name "*_test.py" 2>/dev/null | wc -l)
        if [[ "$test_files" -eq 0 ]]; then
            errors+=("tests/ has no test files (test_*.py)")
        fi
    fi

    # Report results
    if [[ ${#errors[@]} -gt 0 ]]; then
        echo "Template validation failed for: ${template_dir#$PROJECT_DIR/}"
        for err in "${errors[@]}"; do
            echo "  - $err"
        done
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
        echo ""
        echo "Required artifacts:"
        echo "  - pyproject.toml (with name, description)"
        echo "  - Makefile"
        echo "  - .gitignore"
        echo "  - src/<placeholder>/"
        echo "  - tests/ (with test_*.py files)"
        exit 2  # Exit 2 blocks the stop
    fi

    echo "Template validation passed"
    exit 0
}

main
