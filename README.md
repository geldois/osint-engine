# osint-engine

Entity relationship graph engine that expands identifiers into a fully traceable network of connections sourced exclusively from official public records.

## Pre-requisites

- Python v3.12+
- uv

## Setup

```bash
git clone https://github.com/geldois/osint-engine.git
cd osint-engine
uv sync --group dev
uv run pre-commit install
uv run pytest
```
