# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses [Invoke](https://www.pyinvoke.org/) via `uv run invoke` for all common tasks.

```bash
# Install dependencies
uv sync

# Linting
uv run invoke lint          # Fast linting (xenon, ruff, bandit, dodgy, flake8, pydocstyle)
uv run invoke lint.deep     # Slow/detailed linting (mypy, pylint, semgrep)
uv run invoke lint.mypy     # Type checking only
uv run invoke lint.ruff     # Ruff only

# Formatting
uv run invoke style         # Format with docformatter and Ruff

# Tests
uv run invoke test          # Fast tests (excludes @pytest.mark.slow)
uv run invoke test.all      # All tests
uv run invoke test.cov      # Tests with coverage report

# Run a single test
uv run pytest tests/path/to/test_file.py::test_name

# Run the backup
uv run python backup.py

# Run the account mover
uv run python move.py
```

## Architecture

The project is a Zaim (Japanese personal finance app) backup and data manipulation tool. It has two entry points:

- **[backup.py](backup.py)** — Fetches all money transactions via the Zaim API and saves them to `money.csv`
- **[move.py](move.py)** — Moves money entries from one account to another (used for migrating manually-entered records to API-connected account records)

### Package structure (`zaimbackup/`)

- **[config.py](zaimbackup/config.py)** — Loads `config.yml` (OAuth credentials for Zaim API)
- **[backup.py](zaimbackup/backup.py)** — `main()` for the CSV backup flow
- **[move.py](zaimbackup/move.py)** — `Move` orchestrator + `AbstractMove` subclasses (`MoveTransfer`, `MovePayment`, `MoveIncome`) that handle the three Zaim transaction modes
- **[zaim/api/\_\_init\_\_.py](zaimbackup/zaim/api/__init__.py)** — `ZaimApi` subclass of `pyzaim.ZaimAPI` that adds proper typing and lazy OAuth session initialization
- **[zaim/api/cache.py](zaimbackup/zaim/api/cache.py)** — `ZaimCache` caches API responses to `.cache_zaim_api/` (CSV for money, YAML for categories/genres/accounts) to avoid repeated API calls
- **[zaim/api/joiner.py](zaimbackup/zaim/api/joiner.py)** — `Joiner` resolves foreign-key IDs in raw `MoneyTypeDef` records into nested objects, producing `Money` dataclass instances
- **[zaim/api/models/](zaimbackup/zaim/api/models/)** — `TypedDict` and `dataclass` models for money, category, genre, and account

### Data flow

```
ZaimApi (pyzaim wrapper)
  → ZaimCache (caches to .cache_zaim_api/)
    → Joiner (joins IDs → objects, yields Money dataclasses)
      → Move / save_as_csv
```

### Configuration

API credentials go in `config.yml` at the project root (OAuth1 keys for Zaim). To obtain an access token for the first time, run `python -m zaimbackup.zaim.api.access_token`.

### Tooling notes

- `mypy` runs in strict mode
- `ruff` uses `select = ["ALL"]` with a small ignore list; `isort` is set to `force-single-line`
- `flake8` uses `flake8-bugbear` B950 for line length instead of E501
- `docformatter` runs automatically on save (VS Code RunOnSave extension)
- Dev environment runs in Docker via `compose.yml`; the devcontainer config is in `.devcontainer/`
