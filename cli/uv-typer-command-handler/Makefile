.PHONY: install format lint typecheck test run ci clean

install:
	uv tool install . 

reinstall:
	uv tool uninstall mycli
	uv tool install . 
install-dev:
	uv tool install -e . 

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

typecheck:
	uv run ty check src

test:
	uv run pytest tests -v

run:
	uv run mycli

ci: install lint typecheck test

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
