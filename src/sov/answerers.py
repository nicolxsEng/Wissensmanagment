"""AP14: Sichtbare Antwortende – wer zeigt öffentlich, dass er sich auskennt? (plan.md AP14)

Grundlage: Antworten im 7-Tage-Fenster auf klassische Fragen, nur Antworten mit Nutzerkonto.
Nutzer-IDs werden nur intern gezählt; die Ausgabe enthält ausschließlich Aggregate je Jahr.

Kennzahlen (Spalte `metric`):
    answerers                    A1  verschiedene Nutzerkonten mit >= 1 Antwort
    answerers_per_100q               A1 je 100 klassische Fragen
    experts                      A3  Konten mit >= expert_min Antworten (gesamt; je Gruppe: AP07)
    experts_ge2, experts_ge5         Gegenproben für die Schwelle
    top_share_answers            A4  Anteil der Antworten von den aktivsten 10 % der Antwortenden
    continuity                   A5  Anteil der Antwortenden, die schon im Vorjahres-Oktober
                                     geantwortet haben
    answers_without_owner_share      Anteil der Fenster-Antworten ohne Konto (Protokoll)
"""

import math

import polars as pl

from sov import config

OUTPUT_COLUMNS = ("year", "metric", "value")


def window_answers(q: pl.DataFrame, a: pl.DataFrame) -> pl.DataFrame:
    """Antworten im Fenster auf klassische Fragen, mit Jahr der Frage."""
    classic = q.filter(pl.col("is_classic")).select("question_id", "year")
    return a.filter(pl.col("in_window")).join(classic, on="question_id", how="inner")


def _top_share(counts: list[int], share: float) -> float:
    if not counts:
        return float("nan")
    k = max(1, math.ceil(share * len(counts)))
    s = sorted(counts, reverse=True)
    return sum(s[:k]) / sum(s)


def answerer_metrics(
    q: pl.DataFrame,
    a: pl.DataFrame,
    expert_min: int = config.EXPERT_MIN_ANSWERS,
    top_share: float = config.TOP_ANSWERER_SHARE,
) -> pl.DataFrame:
    """Alle Antwortenden-Kennzahlen je Jahr (lange Tabelle year, metric, value)."""
    wa = window_answers(q, a)
    n_q = q.filter(pl.col("is_classic")).group_by("year").agg(n_q=pl.len())
    no_owner = wa.group_by("year").agg(
        answers_without_owner_share=pl.col("owner_user_id").is_null().mean()
    )
    per_user = wa.drop_nulls("owner_user_id").group_by("year", "owner_user_id").agg(n=pl.len())
    lo, hi = config.EXPERT_MIN_ANSWERS_ROBUST
    base = (
        per_user.group_by("year")
        .agg(
            answerers=pl.len(),
            experts=(pl.col("n") >= expert_min).sum(),
            experts_ge2=(pl.col("n") >= lo).sum(),
            experts_ge5=(pl.col("n") >= hi).sum(),
            counts=pl.col("n"),
        )
        .with_columns(
            top_share_answers=pl.col("counts").map_elements(
                lambda c: _top_share(c.to_list(), top_share), return_dtype=pl.Float64
            )
        )
        .drop("counts")
    )
    # Kontinuität: Anteil der Antwortenden in Y, die auch in Y-1 geantwortet haben
    users = per_user.select("year", "owner_user_id")
    prev = users.with_columns(year=(pl.col("year") + 1).cast(users["year"].dtype), seen=pl.lit(1))
    cont = (
        users.join(prev, on=["year", "owner_user_id"], how="left")
        .group_by("year")
        .agg(continuity=pl.col("seen").is_not_null().mean())
    )
    first_year = users["year"].min()
    cont = cont.with_columns(
        continuity=pl.when(pl.col("year") == first_year).then(None).otherwise("continuity")
    )
    wide = (
        base.join(n_q, on="year", how="left")
        .join(no_owner, on="year", how="left")
        .join(cont, on="year", how="left")
        .with_columns(answerers_per_100q=pl.col("answerers") / pl.col("n_q") * 100)
        .drop("n_q")
    )
    return (
        wide.with_columns(pl.exclude("year").cast(pl.Float64))
        .unpivot(index="year", variable_name="metric", value_name="value")
        .drop_nulls("value")
        .sort("metric", "year")
        .select(OUTPUT_COLUMNS)
    )


GROUP_METRICS = ("answerers", "experts", "experts_ge2", "experts_ge5", "answerers_per_100q")


def group_answerer_metrics(
    q: pl.DataFrame,
    a: pl.DataFrame,
    groups: dict[str, list[str]],
    expert_min: int = config.EXPERT_MIN_ANSWERS,
    base_year: int = config.BASE_YEAR,
) -> pl.DataFrame:
    """A2 und A3 je Gruppe: Antwortende und erkennbare Expert:innen auf Fragen der Gruppe.

    Eine Frage gehört zur Gruppe, wenn sie ≥ 1 Tag der Gruppe trägt (wie K7, D07); Fragen mit
    Tags beider Gruppen zählen in beiden. Expert:in = ≥ expert_min Antworten auf Fragen derselben
    Gruppe im selben Oktober. Ausgabe: year, gruppe, metric, value, index (base_year = 100);
    nur Aggregate.
    """
    lo, hi = config.EXPERT_MIN_ANSWERS_ROBUST
    classic = q.filter(pl.col("is_classic"))
    wa = window_answers(q, a).drop_nulls("owner_user_id")
    out = []
    for g, tags in groups.items():
        member = classic.filter(
            pl.col("tags").list.eval(pl.element().is_in(list(tags))).list.any()
        ).select("question_id", "year")
        n_q = member.group_by("year").agg(n_q=pl.len())
        per_user = (
            wa.join(member.select("question_id"), on="question_id", how="semi")
            .group_by("year", "owner_user_id")
            .agg(n=pl.len())
        )
        agg = (
            per_user.group_by("year")
            .agg(
                answerers=pl.len(),
                experts=(pl.col("n") >= expert_min).sum(),
                experts_ge2=(pl.col("n") >= lo).sum(),
                experts_ge5=(pl.col("n") >= hi).sum(),
            )
            .join(n_q, on="year", how="right")
            .fill_null(0)
            .with_columns(answerers_per_100q=pl.col("answerers") / pl.col("n_q") * 100)
            .drop("n_q")
        )
        out.append(
            agg.with_columns(pl.exclude("year").cast(pl.Float64))
            .unpivot(index="year", variable_name="metric", value_name="value")
            .with_columns(gruppe=pl.lit(g))
        )
    long = pl.concat(out)
    base = long.filter(pl.col("year") == base_year).select("gruppe", "metric", base="value")
    return (
        long.join(base, on=["gruppe", "metric"], how="left")
        .with_columns(index=pl.col("value") / pl.col("base") * 100)
        .select("year", "gruppe", "metric", "value", "index")
        .sort("gruppe", "metric", "year")
    )
