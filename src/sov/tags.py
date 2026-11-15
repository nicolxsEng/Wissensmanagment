"""AP03: Kandidaten-Tags, Tag-Zeitreihen und Brüche (Umbenennung, Abschaffung, Entstehung).

Achtung Blindheit (CLAUDE.md Regel 4): Ausgaben mit Fragezahlen je Tag erst nach der
Tag-Kodierung (AP05) ansehen.
"""

import polars as pl

from sov import config


def candidate_tags(
    q: pl.DataFrame, year: int = config.BASE_YEAR, min_count: int = config.MIN_TAG_COUNT
) -> pl.DataFrame:
    """Tags mit >= min_count klassischen Fragen im Oktober `year` (alphabetisch)."""
    return (
        q.filter(pl.col("is_classic") & (pl.col("year") == year))
        .select(pl.col("tags").alias("tag"))
        .explode("tag")
        .drop_nulls()
        .group_by("tag")
        .agg(n=pl.len())
        .filter(pl.col("n") >= min_count)
        .sort("tag")
    )


def tag_year_counts(
    q: pl.DataFrame, tags: list[str], years: list[int] | None = None
) -> pl.DataFrame:
    """Klassische Fragen je Tag und Jahr, fehlende Kombinationen = 0 (tag, year, n)."""
    years = years or config.YEARS
    counts = (
        q.filter(pl.col("is_classic"))
        .select("year", pl.col("tags").alias("tag"))
        .explode("tag")
        .filter(pl.col("tag").is_in(tags))
        .group_by("tag", "year")
        .agg(n=pl.len())
        .with_columns(pl.col("year").cast(pl.Int64))
    )
    grid = pl.DataFrame({"tag": sorted(tags)}).join(
        pl.DataFrame({"year": years}, schema={"year": pl.Int64}), how="cross"
    )
    return (
        grid.join(counts, on=["tag", "year"], how="left")
        .with_columns(pl.col("n").fill_null(0).cast(pl.Int64))
        .sort("tag", "year")
    )


def detect_breaks(
    counts: pl.DataFrame,
    totals: pl.DataFrame,
    min_expected: float = 10,
    drop_ratio: float = 0.1,
    birth_min: int = 10,
) -> pl.DataFrame:
    """Findet Brüche in Tag-Zeitreihen.

    - abbruch: Im Jahr Y hat der Tag weniger als drop_ratio × die Fragen, die bei gleichem
      Anteil wie im Vorjahr zu erwarten wären, und erwartet wären >= min_expected Fragen.
      Der allgemeine Rückgang ist über den Anteil herausgerechnet; die Mindestzahl schützt
      vor Zufallsschwankungen in kleinen Jahren (2025/2026).
    - entsteht: erstes Jahr mit >= birth_min Fragen liegt nach dem Beginn des Trendzeitraums.

    counts: tag, year, n; totals: year, n_year. Rückgabe: tag, kind, year, detail.
    """
    df = (
        counts.join(totals.with_columns(pl.col("year").cast(pl.Int64)), on="year")
        .sort("tag", "year")
        .with_columns(share=pl.col("n") / pl.col("n_year"))
        .with_columns(prev_share=pl.col("share").shift(1).over("tag"))
        .with_columns(expected=pl.col("prev_share") * pl.col("n_year"))
    )
    drops = (
        df.filter(
            (pl.col("expected") >= min_expected) & (pl.col("n") < drop_ratio * pl.col("expected"))
        )
        .group_by("tag")
        .agg(pl.col("year").min())
        .with_columns(
            kind=pl.lit("abbruch"),
            detail=pl.lit("Anteil fällt in einem Jahr auf < 10 % des Vorjahres"),
        )
    )
    births = (
        df.filter(pl.col("n") >= birth_min)
        .group_by("tag")
        .agg(pl.col("year").min())
        .filter(pl.col("year") > config.TREND_START)
        .with_columns(
            kind=pl.lit("entsteht"),
            detail=pl.lit(f"erstes Jahr mit >= {birth_min} Fragen nach {config.TREND_START}"),
        )
    )
    return pl.concat([drops, births]).select("tag", "kind", "year", "detail").sort("tag", "kind")


def synonym_map(synonyms: pl.DataFrame) -> dict[str, str]:
    """from_tag -> to_tag aus data/processed/tag_synonyms.csv."""
    return dict(zip(synonyms["from_tag"], synonyms["to_tag"], strict=True))


def canonicalize(q, mapping: dict[str, str]):
    """Ersetzt Synonym-Tags durch ihren Haupt-Tag (doppelte Tags je Frage entfernt).

    Stack Overflow bildet neue Fragen automatisch auf den Haupt-Tag ab, ältere Fragen behalten
    das alte Synonym. Ohne diesen Schritt entstehen künstliche Sprünge in Tag-Zeitreihen
    (AP03-Protokoll, Entscheidung D15). Funktioniert für DataFrame und LazyFrame.
    """
    return q.with_columns(
        pl.col("tags").list.eval(pl.element().replace(mapping)).list.unique(maintain_order=True)
    )


SYNONYMS_CSV = config.PROCESSED_DIR / "tag_synonyms.csv"


def load_synonym_map() -> dict[str, str]:
    """Synonym-Zuordnung aus AP03 (D15). Fehlt die Datei, zuerst `make tags` ausführen."""
    if not SYNONYMS_CSV.exists():
        raise FileNotFoundError(
            f"{SYNONYMS_CSV} fehlt – zuerst AP03 ausführen (make tags) oder "
            "load_questions(..., canonical_tags=False) verwenden."
        )
    return synonym_map(pl.read_csv(SYNONYMS_CSV))


def canonical_ai_tags(mapping: dict[str, str]) -> list[str]:
    """Die 26 KI-Tags nach Zusammenführung (ein KI-Tag kann selbst Synonym sein)."""
    return sorted({mapping.get(t, t) for t in config.AI_TAGS})
