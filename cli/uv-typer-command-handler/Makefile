
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- 

install: ## install
	uv tool install . --force

reinstall: clean ## reinstall
	@uv tool install . --force --reinstall

install-dev:
	uv tool install -e . 

# --- 

ci: lint types test ## ci

format:
	uv run ruff format .
	uv run ruff check --fix .


lint: ## lint
	uvx ruff check

types: ## types check
	uv run ty check src

test:
	uv run pytest

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# ---

bump-reinstall: bump-version reinstall ## bump version and reinstall

bump-version: ## Bump version 
	@current=$$(grep -E '^version = ' pyproject.toml | sed 's/version = "//;s/"//'); \
	major=$$(echo $$current | cut -d. -f1); \
	minor=$$(echo $$current | cut -d. -f2); \
	patch=$$(echo $$current | cut -d. -f3); \
	new="$$major.$$minor.$$((patch + 1))"; \
	sed -i '' "s/version = \"$$current\"/version = \"$$new\"/" pyproject.toml; \
	echo "vers updated: $$current -> $$new"; \
