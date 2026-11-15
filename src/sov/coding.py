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


# ----------------------------------------------------------------------------- Fragen (AP06)
QUESTION_SHEET_COLUMNS = ("nr", "code", "kategorie", "unsicher", "notiz")


def build_question_sheet(codes: list[str], seed: int) -> pl.DataFrame:
    """Bogen für Fragen: nur Codes in zufälliger Reihenfolge, keine Jahre, Tags oder Zahlen."""
    df = pl.DataFrame({"code": sorted(codes)}).sample(fraction=1.0, shuffle=True, seed=seed)
    return df.with_columns(
        nr=pl.int_range(1, df.height + 1, dtype=pl.Int32),
        kategorie=pl.lit(None, pl.String),
        unsicher=pl.lit(None, pl.String),
        notiz=pl.lit(None, pl.String),
    ).select(QUESTION_SHEET_COLUMNS)


def save_entry(
    path: Path, code: str, kategorie: str, unsicher: bool = False, notiz: str = ""
) -> None:
    """Trägt eine Kodierung in den Bogen ein (überschreibt nur diese eine Zeile)."""
    from sov import config  # noqa: PLC0415

    if kategorie not in config.QUESTION_CATEGORIES:
        raise ValueError(f"Kategorie muss eine von {config.QUESTION_CATEGORIES} sein")
    df = read_sheet(path)
    if code not in df["code"].to_list():
        raise KeyError(code)
    hit = pl.col("code") == code
    df = df.with_columns(
        kategorie=pl.when(hit).then(pl.lit(kategorie)).otherwise("kategorie"),
        unsicher=pl.when(hit).then(pl.lit("x" if unsicher else None)).otherwise("unsicher"),
        notiz=pl.when(hit).then(pl.lit(notiz.strip() or None)).otherwise("notiz"),
    )
    tmp = path.with_suffix(".tmp")
    df.write_csv(tmp, separator=";", include_bom=True)
    tmp.replace(path)  # atomar ersetzen, damit ein Absturz den Bogen nicht beschädigt
