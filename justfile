@lint:
    uv run ruff check --fix build-readme.py
    uv run ruff format build-readme.py

@install:
    uv sync

@run:
    uv run python build-readme.py
