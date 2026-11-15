"""AP02: Kennzahlen TF1/TF3 je Oktober -> data/processed/*.csv + results/metrics_overview.md.

uv run python scripts/02_metrics.py
"""

from datetime import datetime

import polars as pl

from sov import config
from sov.io import load_questions
from sov.metrics import (
    ai_tag_counts,
    changes,
    closed_reasons,
    metrics_long,
    new_type_summary,
    top_tags,
)
from sov.tags import canonical_ai_tags, load_synonym_map

COLS = [
    "year", "tags", "score", "is_classic", "is_new_type", "n_answers_7d", "answered_7d",
    "first_answer_hours", "answered_24h", "accepted_7d", "body_len_nocode", "n_ai_tags",
    "has_code", "is_closed", "closed_reason",
]  # fmt: skip


def de(x: float | None, d: int = 0) -> str:
    if x is None:
        return "–"
    s = f"{x:,.{d}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def overview(long: pl.DataFrame, ch: pl.DataFrame, nt: pl.DataFrame) -> str:
    w = long.filter(pl.col("population") == "klassisch").pivot(
        on="metric", index="year", values="value"
    )
    allq = long.filter(
        (pl.col("population") == "alle") & (pl.col("metric") == "n_questions")
    ).select("year", pl.col("value").alias("n_alle"))
    w = w.join(allq, on="year").sort("year")
    lines = [
        "# Kennzahlen je Oktober (AP02)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Klassische Fragen (ohne neue Fragetypen), "
        "Synonym-Tags zusammengeführt (D15), "
        "Antworten nur im 7-Tage-Fenster. Definitionen: plan.md 5.3.",
        "",
        "| Okt. | Fragen (alle) | klassisch | Antw./Frage | Median | unbeantw. | "
        "Median Std. bis 1. Antw. | in 24 h | akzeptiert | Textlänge | mit Code | "
        "geschlossen | KI-Tag |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in w.to_dicts():
        lines.append(
            f"| {r['year']} | {de(r['n_alle'])} | {de(r['n_questions'])} | "
            f"{de(r['answers_per_q_mean'], 2)} | {de(r['answers_per_q_median'])} | "
            f"{de(100 * r['unanswered_share'], 1)} % | {de(r['first_answer_median_h'], 2)} | "
            f"{de(100 * r['answered_24h_share'], 1)} % | {de(100 * r['accepted_share'], 1)} % | "
            f"{de(r['body_len_median'])} | {de(100 * r['code_share'], 1)} % | "
            f"{de(100 * r['closed_share'], 1)} % | {de(100 * r['ai_share'], 2)} % |"
        )
    names = {
        "n_questions": "Fragen (K1)",
        "answers_per_q_mean": "Antworten je Frage (K2)",
        "unanswered_share": "unbeantwortet (K3)",
        "first_answer_median_h": "Median Std. bis 1. Antwort (K4)",
        "answered_24h_share": "Antwort in 24 h (K5)",
        "accepted_share": "akzeptiert (K6)",
        "body_len_median": "Textlänge (K8)",
        "ai_share": "KI-Tag (K9)",
    }
    lines += [
        "",
        "## Veränderung gegenüber Oktober 2022 (klassische Fragen)",
        "",
        "| Kennzahl | 2022 | 2024 | Δ 2024 | h 2024 | Δ 2025 | Δ 2026 |",
        "|---|---|---|---|---|---|---|",
    ]
    c = ch.filter(pl.col("population") == "klassisch")
    for m, label in names.items():
        sub = {r["compare_year"]: r for r in c.filter(pl.col("metric") == m).to_dicts()}
        share = m.endswith("_share")
        if share:
            nd = 2 if m == "ai_share" else 1
            f = lambda v, nd=nd: f"{de(100 * v, nd)} %"  # noqa: E731
        else:
            nd = 0 if m in ("n_questions", "body_len_median") else 2
            f = lambda v, nd=nd: de(v, nd)  # noqa: E731
        h = sub[2024]["cohens_h"]
        lines.append(
            f"| {label} | {f(sub[2024]['base_value'])} | {f(sub[2024]['compare_value'])} | "
            f"{de(sub[2024]['pct_change'], 1)} % | {de(h, 2) if h is not None else '–'} | "
            f"{de(sub[2025]['pct_change'], 1)} % | {de(sub[2026]['pct_change'], 1)} % |"
        )
    lines += [
        "",
        "Δ = Veränderung in %, h = Cohens h (nur Anteile; |h| ≈ 0,2 klein, 0,5 mittel, "
        "0,8 groß). 2025/2026 nur Bestätigung (kleine Fallzahlen).",
        "",
        "## Neue Fragetypen gegenüber klassischen Fragen (T9)",
        "",
        "| Okt. | Typ | Fragen | Score Ø | Score = 0 | Antw./Frage | unbeantw. | "
        "akzeptiert | geschlossen |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in nt.to_dicts():
        lines.append(
            f"| {r['year']} | {r['typ']} | {de(r['n_questions'])} | {de(r['score_mean'], 2)} | "
            f"{de(100 * r['score_zero_share'], 0)} % | {de(r['answers_per_q_mean'], 2)} | "
            f"{de(100 * r['unanswered_share'], 0)} % | {de(100 * r['accepted_share'], 0)} % | "
            f"{de(100 * r['closed_share'], 0)} % |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    q = load_questions(COLS)
    classic = q.filter(pl.col("is_classic"))
    out = config.PROCESSED_DIR
    out.mkdir(parents=True, exist_ok=True)

    long = metrics_long(q)
    ch = changes(long)
    nt = new_type_summary(q)
    long.write_csv(out / "metrics_yearly.csv")
    ch.write_csv(out / "changes.csv")
    nt.write_csv(out / "new_types.csv")
    ai_tag_counts(classic, canonical_ai_tags(load_synonym_map())).write_csv(
        out / "ai_tags_yearly.csv"
    )
    top_tags(classic, 25).write_csv(out / "top_tags_yearly.csv")
    closed_reasons(classic).write_csv(out / "closed_reasons.csv")

    md = config.RESULTS_DIR / "metrics_overview.md"
    md.write_text(overview(long, ch, nt), encoding="utf-8")
    print(f"Fertig: {out}/metrics_yearly.csv u. a., Übersicht: {md}")


if __name__ == "__main__":
    main()
