"""Kleine Abrufe bei der Stack Exchange API (AP03): Tag-Wikis und Synonyme.

Nutzt ../Datentest/scripts/se_api.py (Key aus ../Datentest/.env, wird nie ausgegeben).
Antworten werden in data/interim/api_cache/ zwischengespeichert, damit jede Anfrage nur
einmal läuft.
"""

import html
import json
import sys
import time
import urllib.parse
from collections.abc import Iterable

import polars as pl

from sov import config

CACHE_DIR = config.INTERIM_DIR / "api_cache"


def _api():
    sys.dont_write_bytecode = True  # keine __pycache__-Dateien im Rohdatenordner anlegen
    path = str(config.SE_API_SCRIPTS)
    if path not in sys.path:
        sys.path.insert(0, path)
    import se_api  # noqa: PLC0415

    return se_api


def _chunks(xs: list[str], n: int = 20) -> Iterable[list[str]]:
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def _fetch_vectorized(endpoint: str, tags: list[str], cache_name: str) -> list[dict]:
    """GET /tags/{tags}/{endpoint} für bis zu 20 Tags je Anfrage (API-Grenze), alle Seiten."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f"{cache_name}.json"
    if cache.exists():
        cached = json.loads(cache.read_text(encoding="utf-8"))
        if cached.get("tags") == sorted(tags):
            return cached["items"]
    api = _api()
    items: list[dict] = []
    n_requests = 0
    for chunk in _chunks(sorted(tags)):
        vec = ";".join(urllib.parse.quote(t, safe="") for t in chunk)
        page = 1
        while True:
            data = api.get(f"tags/{vec}/{endpoint}", page=page, pagesize=100)
            n_requests += 1
            items.extend(data.get("items", []))
            if not data.get("has_more"):
                break
            page += 1
            time.sleep(0.2)
        time.sleep(0.2)
    cache.write_text(
        json.dumps({"tags": sorted(tags), "n_requests": n_requests, "items": items}),
        encoding="utf-8",
    )
    return items


def fetch_wikis(tags: list[str], cache_name: str = "tag_wikis") -> pl.DataFrame:
    """Tag, Auszug aus dem Tag-Wiki (leer, falls kein Wiki)."""
    items = _fetch_vectorized("wikis", tags, cache_name)
    got = {it["tag_name"]: html.unescape(it.get("excerpt") or "").strip() for it in items}
    return pl.DataFrame(
        {"tag": sorted(tags), "wiki_auszug": [got.get(t, "") for t in sorted(tags)]}
    )


def fetch_synonyms(tags: list[str]) -> pl.DataFrame:
    """Synonyme, deren Ziel einer der Tags ist (from_tag -> to_tag)."""
    items = _fetch_vectorized("synonyms", tags, "tag_synonyms")
    schema = {"from_tag": pl.String, "to_tag": pl.String, "applied_count": pl.Int64,
              "creation_date": pl.Int64}  # fmt: skip
    rows = [{k: it.get(k) for k in schema} for it in items]
    df = pl.DataFrame(rows, schema=schema)
    return (
        df.with_columns(created=pl.from_epoch("creation_date", time_unit="s").dt.date())
        .drop("creation_date")
        .sort("to_tag", "from_tag")
    )
