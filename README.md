# forewind-test

CLI for computing financial report fields from applications and reporting data.

## Requirements

- Python `^3.12`
- [Poetry](https://python-poetry.org/)

## Setup

```
pip install poetry           # if not already installed
poetry lock                  # generate poetry.lock from pyproject.toml
poetry install               # create the Poetry-managed venv and install deps
```

## Running tests

```
poetry run pytest tests/
```

## Usage

```
poetry run python app/process.py <data> <application>
```

Example:

```
poetry run python app/process.py src/data.b64 src/applications.b64
```

Both `<data>` and `<application>` are paths to `.b64`-encoded data files (see
`src/data.b64` / `src/applications.b64` for the expected format). The command prints the
resulting table to stdout.