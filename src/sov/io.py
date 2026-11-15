"""Lesen der Rohdaten (../Datentest) und der Parquet-Tabellen aus AP01."""

import gzip
import json
from collections.abc import Iterator
from pathlib import Path

import polars as pl

from sov import config


def raw_year_dir(year: int) -> Path:
    return config.RAW_DIR / str(year)


def iter_jsonl_gz(path: Path) -> Iterator[dict]:
    """Liest gzip-JSONL; mehrere aneinandergehängte gzip-Blöcke sind erlaubt."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def read_progress(year: int) -> dict:
    return json.loads((raw_year_dir(year) / "_progress.json").read_text(encoding="utf-8"))


def load_questions(
    columns: list[str] | None = None, lazy: bool = False, canonical_tags: bool = True
):
    """questions.parquet (eine Zeile je Frage, alle Jahre).

    canonical_tags=True (Standard, D15): Synonym-Tags werden auf ihren Haupt-Tag abgebildet,
    `n_ai_tags` wird mit den zusammengeführten Tags neu berechnet. Rohe Tags nur mit
    canonical_tags=False (z. B. in AP03, das die Synonyme erst ermittelt).
    """
    lf = pl.scan_parquet(config.QUESTIONS_PARQUET)
    if columns:
        lf = lf.select(columns)
    names = lf.collect_schema().names()
    if canonical_tags and "tags" in names:
        from sov.tags import canonical_ai_tags, canonicalize, load_synonym_map

        mapping = load_synonym_map()
        lf = canonicalize(lf, mapping)
        if "n_ai_tags" in names:
            ai = canonical_ai_tags(mapping)
            lf = lf.with_columns(
                n_ai_tags=pl.col("tags").list.eval(pl.element().is_in(ai)).list.sum().cast(pl.Int8)
            )
    return lf if lazy else lf.collect()


def load_answers(columns: list[str] | None = None, lazy: bool = False):
    lf = pl.scan_parquet(config.ANSWERS_PARQUET)
    if columns:
        lf = lf.select(columns)
    return lf if lazy else lf.collect()


def load_texts(columns: list[str] | None = None, lazy: bool = True):
    """texts.parquet ist groß -> standardmäßig lazy."""
    lf = pl.scan_parquet(config.TEXTS_PARQUET)
    if columns:
        lf = lf.select(columns)
    return lf if lazy else lf.collect()
