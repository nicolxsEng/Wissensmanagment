"""AP14: sichtbare Antwortende A1, A3 gesamt, A4, A5 und je Gruppe A2, A3.

uv run python scripts/14_answerers.py

Ausgaben: data/processed/answerers_yearly.csv, data/processed/its_answerers.csv,
results/answerers_overview.md; je Gruppe (Hauptauswertung Runde 2, Gegenproben Runde 1 und
Kern, D26): data/processed/answerers_groups.csv, its_answerers_groups.csv,
results/answerers_groups.md. Nur Aggregate je Jahr; Nutzer-IDs werden nie geschrieben.
"""

from datetime import datetime

import polars as pl

from sov import config
from sov.answerers import answerer_metrics, group_answerer_metrics
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
    groups_part(a, m)


GROUP_NAMES = {
    "answerers": "Antwortende (A2)",
    "answerers_per_100q": "Antwortende je 100 Fragen der Gruppe",
    "experts": f"Erkennbare Expert:innen, ≥ {config.EXPERT_MIN_ANSWERS} Antworten (A3)",
    "experts_ge2": "Gegenprobe Expert:innen ≥ 2",
    "experts_ge5": "Gegenprobe Expert:innen ≥ 5",
}
VARIANT_NAMES = {"runde2": "Runde 2 (Hauptauswertung)", "runde1": "Runde 1 (Gegenprobe)",
                 "kern": "Kern beider Runden (Gegenprobe)"}  # fmt: skip


def groups_part(a: pl.DataFrame, m: pl.DataFrame) -> None:
    """A2/A3 je Gruppe für die drei Gruppenvarianten aus AP07 (D26)."""
    import json

    out = config.PROCESSED_DIR
    r2 = json.loads((out / "groups.json").read_text())
    r1 = json.loads((out / "groups_v1.json").read_text())
    variants = {
        "runde2": {g: r2[g] for g in "GU"},
        "runde1": {g: r1[g] for g in "GU"},
        "kern": {g: sorted(set(r2[g]) & set(r1[g])) for g in "GU"},
    }
    q = load_questions(["question_id", "year", "is_classic", "tags"])
    parts = [
        group_answerer_metrics(q, a, groups).with_columns(variante=pl.lit(v))
        for v, groups in variants.items()
    ]
    g = pl.concat(parts).select("variante", "year", "gruppe", "metric", "value", "index")
    assert not any("user" in c for c in g.columns)
    g.write_csv(out / "answerers_groups.csv")

    fits = []
    for v in variants:
        for grp in "GU":
            for metric in ("answerers", "experts"):
                s = g.filter((pl.col("variante") == v) & (pl.col("gruppe") == grp)
                             & (pl.col("metric") == metric)).sort("year")  # fmt: skip
                fits += [
                    {"variante": v, "gruppe": grp, "metric": metric} | r
                    for r in fit_pretrend(s["year"].to_list(), s["value"].to_list(), "log")
                ]
    fit = pl.DataFrame(fits)
    fit.write_csv(out / "its_answerers_groups.csv")

    def val(v, grp, metric, y, col="index"):
        f = (pl.col("variante") == v) & (pl.col("gruppe") == grp) & (pl.col("metric") == metric)
        return g.filter(f & (pl.col("year") == y))[col].item()

    lines = [
        "# Sichtbare Antwortende je Gruppe (AP14, A2/A3)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Antworten im 7-Tage-Fenster auf klassische "
        "Fragen mit ≥ 1 Tag der Gruppe, nur Antworten mit Konto. Expert:in = ≥ "
        f"{config.EXPERT_MIN_ANSWERS} Antworten auf Fragen derselben Gruppe im selben Oktober. "
        f"Index {config.BASE_YEAR} = 100; Abstand = Index U − Index G. Nur Aggregate.",
        "",
        "## Hauptauswertung (Runde 2)",
        "",
        "| Kennzahl | G 2022 | G 2024 | U 2022 | U 2024 | Index G 2024 | Index U 2024 | "
        "Abstand 2024 | Abstand 2025 | Abstand 2026 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for metric, label in GROUP_NAMES.items():
        d = 1 if metric == "answerers_per_100q" else 0
        dist = [val("runde2", "U", metric, y) - val("runde2", "G", metric, y)
                for y in config.POST_YEARS[1:]]  # fmt: skip
        lines.append(
            f"| {label} | {de(val('runde2', 'G', metric, 2022, 'value'), d)} | "
            f"{de(val('runde2', 'G', metric, 2024, 'value'), d)} | "
            f"{de(val('runde2', 'U', metric, 2022, 'value'), d)} | "
            f"{de(val('runde2', 'U', metric, 2024, 'value'), d)} | "
            f"{de(val('runde2', 'G', metric, 2024), 1)} | "
            f"{de(val('runde2', 'U', metric, 2024), 1)} | "
            + " | ".join(
                f"**{de(x, 1, sign=True)}**" if i == 0 else de(x, 1, sign=True)
                for i, x in enumerate(dist)
            )  # fmt: skip
            + " |"
        )
    a1 = dict(m.filter(pl.col("metric") == "answerers").select("year", "value").iter_rows())
    share_idx = {
        grp: val("runde2", grp, "answerers", 2024, "value")
        / a1[2024]
        / (val("runde2", grp, "answerers", 2022, "value") / a1[2022])
        * 100
        for grp in "GU"
    }
    lines += [
        "",
        "Zum Vergleich mit AP07 (Anteil statt Anzahl, allgemeiner Rückgang herausgerechnet): "
        "Anteil der Antwortenden einer Gruppe an allen sichtbaren Antwortenden (A1), Index 2024: "
        f"G {de(share_idx['G'], 1)}, U {de(share_idx['U'], 1)}, Abstand "
        f"{de(share_idx['U'] - share_idx['G'], 1, sign=True)}.",
    ]
    lines += ["", "## Gegenproben (Abstand 2024, Index U − Index G)", "",
              "| Variante | Antwortende (A2) | Expert:innen ≥ 3 (A3) | ≥ 2 | ≥ 5 |",
              "|---|---|---|---|---|"]  # fmt: skip
    for v, name in VARIANT_NAMES.items():
        cells = [de(val(v, "U", m_, 2024) - val(v, "G", m_, 2024), 1, sign=True)
                 for m_ in ("answerers", "experts", "experts_ge2", "experts_ge5")]  # fmt: skip
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines += ["", "## Abweichung vom Trend 2015–2022 (Log-Skala, Hauptauswertung)", "",
              "| Gruppe | Kennzahl | 2023 | 2024 | 2025 | 2026 |",
              "|---|---|---|---|---|---|"]  # fmt: skip
    for grp in "GU":
        for metric in ("answerers", "experts"):
            rows = {r["year"]: r for r in fit.filter(
                (pl.col("variante") == "runde2") & (pl.col("gruppe") == grp)
                & (pl.col("metric") == metric)).to_dicts()}  # fmt: skip

            def cell(y: int, rows=rows) -> str:
                r = rows[y]
                mark = {"darunter": " ▼", "darüber": " ▲"}.get(r["outside_pi"], "")
                return f"{de(r['deviation_pct'], 0, sign=True)} %{mark}"

            lines.append(f"| {grp} | {GROUP_NAMES[metric]} | "
                         + " | ".join(cell(y) for y in config.POST_YEARS) + " |")  # fmt: skip
    lines += [
        "",
        "Lesehilfe: Die Zahl der Antwortenden folgt mechanisch der Zahl der Fragen einer Gruppe. "
        "Der Index-Abstand vergleicht beide Gruppen unter derselben Mechanik; ein positiver "
        "Abstand heißt: Bei Umgebungs-Fragen bleiben anteilig mehr Antwortende bzw. "
        "Expert:innen sichtbar als bei Grundlagen-Fragen. 2025/2026 nur Bestätigung "
        "(kleine Fallzahlen).",
    ]
    md = config.RESULTS_DIR / "answerers_groups.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
