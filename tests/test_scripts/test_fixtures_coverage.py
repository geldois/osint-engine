from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).parents[2]
_PROVIDERS = _ROOT / "src" / "osint_engine" / "infrastructure" / "providers"
_URL_SUFFIX = re.compile(r'url_suffix="([^"]+)"')
_PAID_PROVIDER = "kipflow"
_FETCHERS = sorted(
    path
    for path in _PROVIDERS.glob("*/**/*_fetcher.py")
    if path.relative_to(_PROVIDERS).parts[0] != _PAID_PROVIDER
)


@pytest.mark.parametrize("fetcher", _FETCHERS, ids=lambda path: path.name)
def test_every_free_fetcher_endpoint_has_a_fixtures_case(fetcher: Path) -> None:
    fixtures_source = (_ROOT / "scripts" / "fixtures.py").read_text(encoding="utf-8")
    suffixes = _URL_SUFFIX.findall(fetcher.read_text(encoding="utf-8"))

    missing = [suffix for suffix in suffixes if f'"{suffix}"' not in fixtures_source]

    assert not missing
