"""AP14 (Teil ohne Gruppen): sichtbare Antwortende A1, A3 gesamt, A4, A5.

uv run python scripts/14_answerers.py

Ausgaben: data/processed/answerers_yearly.csv, data/processed/its_answerers.csv,
results/answerers_overview.md. Je Gruppe (A2, A3 nach G/U) folgt nach AP05/AP07.
Nur Aggregate je Jahr; Nutzer-IDs werden nie geschrieben.
"""

from datetime import datetime

import polars as pl

from sov import config
from sov.answerers import answerer_metrics
from sov.io import load_answers, load_questions
from sov.its import fit_pretrend

ITS_METRICS = {
    "answerers": "log",
    "answerers_per_100q": "log",
    "experts": "log",
    "top_share_answers": "logit",
    "continuity": "logit",
}
NAMES = {
    "answerers": "Sichtbare Antwortende (A1)",
    "answerers_per_100q": "Antwortende je 100 Fragen",
    "experts": f"Erkennbare Expert:innen, ≥ {config.EXPERT_MIN_ANSWERS} Antworten (A3)",
    "top_share_answers": "Antworten der aktivsten 10 % (A4)",
    "continuity": "Schon im Vorjahr aktiv (A5)",
}


def de(x: float | None, d: int = 0, sign: bool = False) -> str:
    if x is None:
        return "–"
    s = f"{x:+,.{d}f}" if sign else f"{x:,.{d}f}"
    s = s.replace(",", " ").replace(".", ",").replace(" ", ".")
    return s.replace("-", "−")


def fmt(metric: str, v: float | None) -> str:
    if v is None:
        return "–"
    if metric in ("top_share_answers", "continuity", "answers_without_owner_share"):
        return f"{de(100 * v, 1)} %"
    return de(v, 1 if metric == "answerers_per_100q" else 0)


def main() -> None:
    q = load_questions(["question_id", "year", "is_classic"], canonical_tags=False)
    a = load_answers(["question_id", "owner_user_id", "in_window"])
    m = answerer_metrics(q, a)
    assert not any("user" in c for c in m.columns)
    out = config.PROCESSED_DIR
    m.write_csv(out / "answerers_yearly.csv")

    fits = []
    for metric, scale in ITS_METRICS.items():
        s = m.filter(pl.col("metric") == metric).sort("year")
        fits += [
            {"metric": metric, "scale": scale} | r
            for r in fit_pretrend(s["year"].to_list(), s["value"].to_list(), scale)
        ]
    fit = pl.DataFrame(fits)
    fit.write_csv(out / "its_answerers.csv")

    w = m.pivot(on="metric", index="year", values="value").sort("year")
    cols = ["answerers", "answerers_per_100q", "experts", "top_share_answers", "continuity",
            "answers_without_owner_share"]  # fmt: skip
    lines = [
        "# Sichtbare Antwortende (AP14, Teil ohne Gruppen)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Antworten im 7-Tage-Fenster auf klassische "
        "Fragen, nur Antworten mit Nutzerkonto. Nur Aggregate; keine Nutzer-IDs.",
        "",
        "| Okt. | Antwortende | je 100 Fragen | Expert:innen (≥ 3) | Anteil Top 10 % | "
        "Vorjahr aktiv | ohne Konto |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in w.to_dicts():
        lines.append(f"| {r['year']} | " + " | ".join(fmt(c, r.get(c)) for c in cols) + " |")
    lines += [
        "",
        "## Abweichung vom Trend 2015–2022",
        "",
        "▼ / ▲ = außerhalb des 95-%-Vorhersageintervalls. 2025/2026 nur Bestätigung.",
        "",
        "| Kennzahl | 2024 erwartet | 2024 beob. | 2023 | 2024 | 2025 | 2026 |",
        "|---|---|---|---|---|---|---|",
    ]
    for metric, label in NAMES.items():
        rows = {r["year"]: r for r in fit.filter(pl.col("metric") == metric).to_dicts()}

        def cell(y: int, rows=rows) -> str:
            r = rows[y]
            mark = {"darunter": " ▼", "darüber": " ▲"}.get(r["outside_pi"], "")
            return f"{de(r['deviation_pct'], 0, sign=True)} %{mark}"

        lines.append(
            f"| {label} | {fmt(metric, rows[2024]['expected'])} | "
            f"{fmt(metric, rows[2024]['observed'])} | "
            + " | ".join(cell(y) for y in config.POST_YEARS)
            + " |"
        )
    lines += [
        "",
        "Lesehilfe: Alle Antwortenden-Kennzahlen hängen mechanisch an der Zahl der Fragen. "
        "Weniger Fragen bedeuten weniger Antwortende und weniger Personen mit ≥ 3 Antworten; "
        "zugleich steigen die Antwortenden je 100 Fragen, weil sich die Antworten auf weniger "
        "Fragen je Person verteilen, und die Konzentration sinkt. Für sich genommen sind diese "
        "Verläufe deshalb nur beschreibend. Belastbar wird AP14 im Vergleich der Gruppen "
        "Grundlagen/Umgebung (A2, A3): Beide Gruppen unterliegen derselben Mechanik.",
    ]
    md = config.RESULTS_DIR / "answerers_overview.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    a22 = m.filter((pl.col("year") == 2022) & (pl.col("metric") == "answerers"))["value"].item()
    print(f"Fertig. A1 2022 = {a22:,.0f} (Vorabprüfung: 30.538). Übersicht: {md}")


if __name__ == "__main__":
    main()
