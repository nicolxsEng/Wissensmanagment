"""Kodierbögen für die menschliche Kodierung (AP04, später AP06).

Bögen sind CSV mit Semikolon und UTF-8-BOM, damit Excel und Numbers sie direkt richtig
öffnen. Ein Bogen, in dem schon etwas eingetragen ist, wird nie überschrieben.
"""

from pathlib import Path

import polars as pl

SHEET_COLUMNS = ("nr", "tag", "wiki_auszug", "kategorie", "unsicher", "notiz")
ENTRY_COLUMNS = ("kategorie", "unsicher", "notiz")


def build_tag_sheet(wiki: pl.DataFrame, seed: int) -> pl.DataFrame:
    """Bogen mit allen Tags in zufälliger Reihenfolge (eigener Seed je Person), ohne Zahlen."""
    shuffled = (
        wiki.select("tag", "wiki_auszug").sort("tag").sample(fraction=1.0, shuffle=True, seed=seed)
    )
    return shuffled.with_columns(
        nr=pl.int_range(1, shuffled.height + 1, dtype=pl.Int32),
        kategorie=pl.lit(None, pl.String),
        unsicher=pl.lit(None, pl.String),
        notiz=pl.lit(None, pl.String),
    ).select(SHEET_COLUMNS)


def read_sheet(path: Path) -> pl.DataFrame:
    return pl.read_csv(path, separator=";", infer_schema=False).with_columns(
        pl.col("nr").cast(pl.Int32)
    )


def sheet_has_entries(path: Path) -> bool:
    """True, wenn in einer Eingabespalte schon irgendetwas steht."""
    if not path.exists():
        return False
    df = read_sheet(path)
    cols = [c for c in ENTRY_COLUMNS if c in df.columns]
    return any(df[c].fill_null("").str.strip_chars().str.len_chars().sum() > 0 for c in cols)


def write_sheet(sheet: pl.DataFrame, path: Path) -> None:
    """Schreibt einen leeren Bogen; bricht ab, falls dort schon kodiert wurde."""
    if sheet_has_entries(path):
        raise FileExistsError(f"{path} enthält bereits Einträge und wird nicht überschrieben.")
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.write_csv(path, separator=";", include_bom=True)
