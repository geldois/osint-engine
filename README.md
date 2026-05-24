# corporate-risk-engine

An asynchronous Python API designed for public security intelligence, cross-referencing corporate data from multiple external APIs to detect corruption indicators.

# Run

## On Linux

```bash
git clone https://github.com/geldois/corporate-risk-engine.git && cd corporate-risk-engine
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## On Windows

```shell
git clone https://github.com/geldois/corporate-risk-engine.git
cd corporate-risk-engine
python -m venv .venv
.venv/Scripts/Activate
pip install -e ".[dev]"
pre-commit install
```
