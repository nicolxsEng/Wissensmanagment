"""AP09: Übereinstimmung der Kodierinstanzen bei den 600 Fragen, Konsens, Prüfstichprobe.

uv run python scripts/09_question_agreement.py

Eingabe: coding/questions/llm_fragen_<modell>.csv (AP16)
Ausgaben: results/agreement_questions.md, coding/questions/labels_600.csv (nur Konsens),
          coding/pruefung/fragen_100.csv (Prüfung in der Kodier-App, Bogen „Prüfung“)
"""

from datetime import datetime

import polars as pl

from sov import config
from sov.agreement import crosstab, kappa_ci, landis_koch
from sov.coding import CHECK_COLUMNS, build_check_sheet, read_sheet, write_sheet

N_CHECK = 100


def main() -> None:
    k1, k2 = config.LLM_CODERS
    a = read_sheet(config.CODING_DIR / "questions" / f"llm_fragen_{k1}.csv")
    b = read_sheet(config.CODING_DIR / "questions" / f"llm_fragen_{k2}.csv")
    df = a.join(b, on="code", suffix="_b")
    split = pl.read_csv(config.CODING_DIR / "questions" / "split.csv")
    df = df.join(split, on="code")
    cats = list(config.QUESTION_CATEGORIES)
    ka = kappa_ci(df["kategorie"].to_list(), df["kategorie_b"].to_list(), cats)
    agree = df.filter(pl.col("kategorie") == pl.col("kategorie_b"))
    agree.select("code", pl.col("kategorie").alias("label"), "split").write_csv(
        config.CODING_DIR / "questions" / "labels_600.csv"
    )
    ct = crosstab(df["kategorie"].to_list(), df["kategorie_b"].to_list(), cats, k1, k2)
    per_split = agree.group_by("split").len().sort("split").to_dicts()
    dist = agree.group_by("kategorie").len().sort("kategorie").to_dicts()
    crit = "erfüllt" if ka["kappa"] >= config.KAPPA_MIN else "NICHT erfüllt"
    lines = [
        "# Einordnung der Fragen – Übereinstimmung (AP09)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Kodierinstanzen: "
        f"{config.LLM_MODELS[k1]} und {config.LLM_MODELS[k2]} (AP16).",
        "",
        f"- Fragen: {df.height}",
        f"- Cohens Kappa: **{ka['kappa']:.2f}** [{ka['ci_low']:.2f}; {ka['ci_high']:.2f}] "
        f"({landis_koch(ka['kappa'])}), Übereinstimmung {ka['uebereinstimmung']:.0%}",
        f"- Kriterium ≥ {config.KAPPA_MIN}: {crit}",
        f"- Konsens (Referenz für AP10): {agree.height} Fragen "
        f"({', '.join(f'{r["split"]}: {r["len"]}' for r in per_split)}); "
        f"Verteilung {', '.join(f'{r["kategorie"]} {r["len"]}' for r in dist)}",
        "",
        f"Kreuztabelle (Zeilen {k1}, Spalten {k2}):",
        "",
        "| | " + " | ".join(cats) + " |",
        "|---|" + "---|" * len(cats),
    ]
    for r in ct.to_dicts():
        lines.append(f"| {r[k1]} | " + " | ".join(str(r[c]) for c in cats) + " |")
    (config.RESULTS_DIR / "agreement_questions.md").write_text("\n".join(lines) + "\n",
                                                              encoding="utf-8")  # fmt: skip
    pool = agree.select("code", "kategorie", "begruendung")
    (config.CODING_DIR / "pruefung").mkdir(parents=True, exist_ok=True)
    write_sheet(
        build_check_sheet(pool, "code", N_CHECK, config.SEED + 60),
        config.CODING_DIR / "pruefung" / "fragen_100.csv",
        entry_cols=CHECK_COLUMNS,
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
