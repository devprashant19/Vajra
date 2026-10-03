setup:
    uv sync
    pnpm install -r
    pre-commit install

lint:
    uv run ruff check .
    uv run mypy .
    pnpm -r run lint

format:
    uv run ruff format .
    pnpm -r run format

typecheck:
    uv run mypy .
    pnpm -r run typecheck

test-fast:
    uv run pytest -m "not slow and not gpu and not live"
    pnpm -r run test

test-all:
    uv run pytest
    pnpm -r run test

up-lite:
    docker compose --profile lite up -d

up-full:
    docker compose --profile full up -d

down:
    docker compose down

clean:
    rm -rf build dist .pytest_cache .mypy_cache .ruff_cache

demo:
    docker compose --profile demo up -d

bundles:
    uv run python tools/write_bundles.py


