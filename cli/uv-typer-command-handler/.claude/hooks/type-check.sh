#!/bin/bash
# PostToolUse hook: Run ty type checker after Write/Edit on Python files

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only check Python files in src or tests
if [[ ! "$FILE_PATH" =~ \.(py)$ ]]; then
  exit 0
fi

if [[ ! "$FILE_PATH" =~ (src/*|tests)/ ]]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR" || exit 0

# Run ty type checker
RESULT=$(make types 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  exit 0
fi

# Extract compact error summaries: "file:line — error message"
ERRORS=$(echo "$RESULT" | awk '
  /^error\[/ { msg = $0 }
  /^   --> / {
    loc = $2
    if (msg != "") print loc " — " msg
    msg = ""
  }
')

ERROR_COUNT=$(echo "$ERRORS" | grep -c .)
MAX_SHOWN=5

if [ "$ERROR_COUNT" -le "$MAX_SHOWN" ]; then
  echo "Type check: $ERROR_COUNT error(s)" >&2
  echo "$ERRORS" >&2
else
  echo "Type check: $ERROR_COUNT error(s) (showing first $MAX_SHOWN)" >&2
  echo "$ERRORS" | head -n "$MAX_SHOWN" >&2
  echo "... and $((ERROR_COUNT - MAX_SHOWN)) more. Run 'make types' for full output." >&2
fi

exit 2
