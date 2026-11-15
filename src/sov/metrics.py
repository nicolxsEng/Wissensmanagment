"""AP02: Kennzahlen K1–K9 je Oktober (plan.md 5.3) und Veränderungen (plan.md 5.4).

Anteile werden als Anteil (0–1) gespeichert, nicht in Prozent. Metriknamen:

    n_questions            K1  Anzahl Fragen
    answers_per_q_mean     K2  Antworten im Fenster je Frage, Mittelwert
    answers_per_q_median   K2  … Median
    unanswered_share       K3  Anteil ohne Antwort im Fenster
    first_answer_median_h  K4  Median Stunden bis zur ersten Antwort (nur beantwortete)
    answered_24h_share     K5  Anteil mit erster Antwort <= 24 h
    accepted_share         K6  Anteil mit akzeptierter Antwort aus dem Fenster
    body_len_median        K8  Median Zeichen ohne Codeblöcke (dazu q25, q75)
    ai_share               K9  Anteil mit >= 1 KI-Tag
    code_share, closed_share   Zusatz (Abbildungen, Gegenproben)

Populationen: klassisch (Hauptauswertung), score_ge_1 (Gegenprobe), alle und neue_typen
(nur n_questions, D03).
"""

import math

import polars as pl

from sov import config

SHARE_METRICS = frozenset(
    {
        "unanswered_share",
        "answered_24h_share",
        "accepted_share",
        "ai_share",
        "code_share",
        "closed_share",
    }
)


def yearly_metrics(q: pl.DataFrame) -> pl.DataFrame:
    """Alle Kennzahlen je Jahr für eine bereits gefilterte Population (breite Tabelle)."""
    return (
        q.group_by("year")
        .agg(
            n_questions=pl.len(),
            answers_per_q_mean=pl.col("n_answers_7d").mean(),
            answers_per_q_median=pl.col("n_answers_7d").median(),
            unanswered_share=(~pl.col("answered_7d")).mean(),
            first_answer_median_h=pl.col("first_answer_hours")
            .filter(pl.col("answered_7d"))
            .median(),
            answered_24h_share=pl.col("answered_24h").mean(),
            accepted_share=pl.col("accepted_7d").mean(),
            body_len_median=pl.col("body_len_nocode").median(),
            body_len_q25=pl.col("body_len_nocode").quantile(0.25, "linear"),
            body_len_q75=pl.col("body_len_nocode").quantile(0.75, "linear"),
            ai_share=(pl.col("n_ai_tags") > 0).mean(),
            code_share=pl.col("has_code").mean(),
            closed_share=pl.col("is_closed").mean(),
        )
        .sort("year")
    )


def _to_long(wide: pl.DataFrame, population: str) -> pl.DataFrame:
    return (
        wide.with_columns(pl.exclude("year").cast(pl.Float64))
        .unpivot(index="year", variable_name="metric", value_name="value")
        .with_columns(population=pl.lit(population))
        .select("year", "population", "metric", "value")
    )


def metrics_long(q: pl.DataFrame) -> pl.DataFrame:
    """Lange Tabelle year, population, metric, value für alle Populationen."""
    classic = q.filter(pl.col("is_classic"))
    parts = [
        _to_long(yearly_metrics(classic), "klassisch"),
        _to_long(yearly_metrics(classic.filter(pl.col("score") >= 1)), "score_ge_1"),
    ]
    for name, sub in (("alle", q), ("neue_typen", q.filter(pl.col("is_new_type")))):
        counts = sub.group_by("year").agg(n_questions=pl.len())
        parts.append(_to_long(counts, name))
    return pl.concat(parts).sort("population", "metric", "year")


def cohens_h(p1: float, p2: float) -> float:
    """Effektstärke für zwei Anteile: h = 2·asin(√p2) − 2·asin(√p1)."""
    return 2 * math.asin(math.sqrt(p2)) - 2 * math.asin(math.sqrt(p1))


def changes(
    long: pl.DataFrame,
    base_year: int = config.BASE_YEAR,
    compare_years: list[int] | None = None,
) -> pl.DataFrame:
    """Veränderung base_year -> compare_year in %, für Anteile zusätzlich Cohens h."""
    compare_years = compare_years or config.POST_YEARS
    base = long.filter(pl.col("year") == base_year).select(
        "population", "metric", pl.col("value").alias("base_value")
    )
    comp = long.filter(pl.col("year").is_in(compare_years)).select(
        "population", "metric", pl.col("year").alias("compare_year"), "value"
    )
    out = comp.join(base, on=["population", "metric"], how="inner").with_columns(
        base_year=pl.lit(base_year),
        pct_change=(pl.col("value") / pl.col("base_value") - 1) * 100,
    )
    h = [
        cohens_h(r["base_value"], r["value"]) if r["metric"] in SHARE_METRICS else None
        for r in out.select("metric", "base_value", "value").to_dicts()
    ]
    return (
        out.with_columns(cohens_h=pl.Series(h, dtype=pl.Float64))
        .select(
            "population",
            "metric",
            "base_year",
            "compare_year",
            "base_value",
            pl.col("value").alias("compare_value"),
            "pct_change",
            "cohens_h",
        )  # fmt: skip
        .sort("population", "metric", "compare_year")
    )


# ----------------------------------------------------------------------------- Tags
def tag_counts(q: pl.DataFrame) -> pl.DataFrame:
    """Fragen je Jahr und Tag, mit Anteil an allen Fragen des Jahres (Population wie q)."""
    totals = q.group_by("year").agg(n_year=pl.len())
    return (
        q.select("year", "tags")
        .explode("tags")
        .drop_nulls("tags")
        .group_by("year", pl.col("tags").alias("tag"))
        .agg(n=pl.len())
        .join(totals, on="year")
        .with_columns(share=pl.col("n") / pl.col("n_year"))
        .drop("n_year")
    )


def top_tags(q: pl.DataFrame, n: int = 25) -> pl.DataFrame:
    return (
        tag_counts(q)
        .with_columns(rank=pl.col("n").rank("ordinal", descending=True).over("year"))
        .filter(pl.col("rank") <= n)
        .sort("year", "rank")
        .select("year", "rank", "tag", "n", "share")
    )


def ai_tag_counts(q: pl.DataFrame) -> pl.DataFrame:
    """Fragen je Jahr und KI-Tag (alle 26 Tags, fehlende Kombinationen = 0)."""
    tc = tag_counts(q).filter(pl.col("tag").is_in(sorted(config.AI_TAGS)))
    grid = pl.DataFrame({"year": config.YEARS}, schema={"year": pl.Int16}).join(
        pl.DataFrame({"tag": sorted(config.AI_TAGS)}), how="cross"
    )
    return (
        grid.join(tc, on=["year", "tag"], how="left")
        .with_columns(pl.col("n").fill_null(0), pl.col("share").fill_null(0.0))
        .sort("year", "tag")
    )


# ----------------------------------------------------------------------------- neue Fragetypen
def new_type_summary(q: pl.DataFrame) -> pl.DataFrame:
    """Neue Fragetypen und klassische Fragen 2025/2026 nebeneinander (Tabelle T9)."""
    years = [y for y in config.YEARS if y >= config.NEW_TYPE_START.year]
    sub = q.filter(pl.col("year").is_in(years)).with_columns(
        typ=pl.when(~pl.col("is_new_type"))
        .then(pl.lit("klassisch"))
        .when(pl.col("tags").list.contains("advice"))
        .then(pl.lit("advice"))
        .otherwise(pl.lit("best-practices"))
    )
    return (
        sub.group_by("year", "typ")
        .agg(
            n_questions=pl.len(),
            score_mean=pl.col("score").mean(),
            score_zero_share=(pl.col("score") == 0).mean(),
            answers_per_q_mean=pl.col("n_answers_7d").mean(),
            unanswered_share=(~pl.col("answered_7d")).mean(),
            accepted_share=pl.col("accepted_7d").mean(),
            closed_share=pl.col("is_closed").mean(),
            body_len_median=pl.col("body_len_nocode").median(),
        )
        .sort("year", "typ")
    )


def closed_reasons(q: pl.DataFrame) -> pl.DataFrame:
    """Schließungsgründe je Jahr (klassische Fragen), Anteil an allen Fragen des Jahres."""
    totals = q.group_by("year").agg(n_year=pl.len())
    return (
        q.filter(pl.col("is_closed"))
        .group_by("year", "closed_reason")
        .agg(n=pl.len())
        .join(totals, on="year")
        .with_columns(share=pl.col("n") / pl.col("n_year"))
        .drop("n_year")
        .sort("year", "n", descending=[False, True])
    )
