"""AP08: Unterbrochene Zeitreihe für die TF1-Kennzahlen (plan.md 5.5).

uv run python scripts/08_its.py

Eingabe: data/processed/metrics_yearly.csv (AP02)
Ausgaben: data/processed/its_fit.csv, its_segmented.csv, results/its_overview.md
Gruppenanteile (TF2) folgen in AP07 mit denselben Funktionen.
"""

from datetime import datetime

import polars as pl

from sov import config
from sov.its import TF1_METRICS, fit_pretrend, segmented

POPULATIONS = ("klassisch", "score_ge_1")
NAMES = {
    "n_questions": "Fragen (K1)",
    "answers_per_q_mean": "Antworten je Frage (K2)",
    "unanswered_share": "unbeantwortet (K3)",
    "first_answer_median_h": "Std. bis 1. Antwort (K4)",
    "answered_24h_share": "Antwort in 24 h (K5)",
    "accepted_share": "akzeptiert (K6)",
    "body_len_median": "Textlänge (K8)",
}


def de(x: float, d: int = 1, sign: bool = False) -> str:
    s = f"{x:+,.{d}f}" if sign else f"{x:,.{d}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def fmt_value(metric: str, v: float) -> str:
    if metric.endswith("_share"):
        return f"{de(100 * v)} %"
    if metric == "n_questions":
        return de(v, 0)
    if metric == "body_len_median":
        return de(v, 0)
    return de(v, 2)


def run() -> tuple[pl.DataFrame, pl.DataFrame]:
    m = pl.read_csv(config.PROCESSED_DIR / "metrics_yearly.csv")
    fits, segs = [], []
    for pop in POPULATIONS:
        for metric, scale in TF1_METRICS.items():
            s = m.filter((pl.col("population") == pop) & (pl.col("metric") == metric)).sort("year")
            years, values = s["year"].to_list(), s["value"].to_list()
            base = {"population": pop, "metric": metric, "scale": scale}
            fits += [base | r for r in fit_pretrend(years, values, scale)]
            segs += [base | r for r in segmented(years, values, scale)]
    return pl.DataFrame(fits), pl.DataFrame(segs)


def overview(fit: pl.DataFrame, seg: pl.DataFrame) -> str:
    lines = [
        "# Unterbrochene Zeitreihe – TF1 (AP08)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Trend geschätzt auf Oktober "
        f"{config.TREND_START}–{config.BASE_YEAR} (8 Punkte), fortgeschrieben auf 2023–2026. "
        "Log-Skala für Zählungen, Wartezeit, Länge; Logit-Skala für Anteile. Klassische Fragen, "
        "Antworten im 7-Tage-Fenster, Synonyme zusammengeführt.",
        "",
        "## Abweichung vom Trend (beobachtet / erwartet − 1)",
        "",
        "▼ / ▲ = Wert liegt unter / über dem 95-%-Vorhersageintervall der Fortschreibung. "
        "2025/2026 nur Bestätigung (kleine Fallzahlen).",
        "",
    ]
    for pop, title in (("klassisch", "Hauptauswertung"), ("score_ge_1", "Gegenprobe Score ≥ 1")):
        lines += [
            f"### {title}",
            "",
            "| Kennzahl | 2022 beob. | 2024 erwartet | 2024 beob. | 2023 | 2024 | 2025 | 2026 |",
            "|---|---|---|---|---|---|---|---|",
        ]
        f = fit.filter(pl.col("population") == pop)
        for metric, label in NAMES.items():
            rows = {r["year"]: r for r in f.filter(pl.col("metric") == metric).to_dicts()}

            def cell(y: int, rows=rows) -> str:
                r = rows[y]
                mark = {"darunter": " ▼", "darüber": " ▲"}.get(r["outside_pi"], "")
                return f"{de(r['deviation_pct'], 0, sign=True)} %{mark}"

            lines.append(
                f"| {label} | {fmt_value(metric, rows[2022]['observed'])} | "
                f"{fmt_value(metric, rows[2024]['expected'])} | "
                f"{fmt_value(metric, rows[2024]['observed'])} | "
                + " | ".join(cell(y) for y in (2023, 2024, 2025, 2026))
                + " |"
            )
        lines.append("")
    lines += [
        "## Segmentierte Regression (Ergänzung, 2015–2026, 12 Punkte)",
        "",
        "Niveau = Abweichung im Jahr 2023 gegenüber dem fortgeschriebenen Trend; "
        "Steigung = Änderung der "
        "jährlichen Veränderung danach. Bei Zählungen/Längen als Faktor, bei Anteilen als "
        "Odds Ratio, jeweils mit 95-%-KI. Nur beschreibend.",
        "",
        "| Kennzahl | Trend vorher je Jahr | Niveausprung | Steigungsänderung |",
        "|---|---|---|---|",
    ]
    s = seg.filter(pl.col("population") == "klassisch")
    for metric, label in NAMES.items():
        t = {r["term"]: r for r in s.filter(pl.col("metric") == metric).to_dicts()}

        def eff(term: str, t=t) -> str:
            r = t[term]
            return f"{de(r['effect'], 2)} [{de(r['effect_low'], 2)}; {de(r['effect_high'], 2)}]"

        lines.append(f"| {label} | {eff('trend')} | {eff('niveau')} | {eff('steigung')} |")
    lines += [
        "",
        "Lesehilfe: Faktor 0,50 beim Niveausprung der Fragen = nach dem Schnitt halb so viele "
        "Fragen, wie der Trend erwarten ließ. Odds Ratio > 1 bei „unbeantwortet“ = höherer "
        "Anteil als erwartet.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    fit, seg = run()
    out = config.PROCESSED_DIR
    fit.write_csv(out / "its_fit.csv")
    seg.write_csv(out / "its_segmented.csv")
    md = config.RESULTS_DIR / "its_overview.md"
    md.write_text(overview(fit, seg), encoding="utf-8")
    print(f"Fertig: {out / 'its_fit.csv'}, {out / 'its_segmented.csv'}, Übersicht: {md}")


if __name__ == "__main__":
    main()
