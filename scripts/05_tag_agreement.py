"""AP05: Übereinstimmung der beiden Kodierinstanzen bei den Tags, Gruppen, Prüfstichprobe.

uv run python scripts/05_tag_agreement.py

Eingabe: coding/tags/llm_tags_<modell>.csv (AP16) für die zwei Modelle aus config.LLM_CODERS
Ausgaben: results/agreement_tags.md, data/processed/groups.json,
          coding/pruefung/tags_40.csv (Prüfung durch die Autor:innen, Spalte `stimmt` j/n)
Runde 1 (Prompt v1) ist gesichert: data/processed/groups_v1.json, coding/tags/llm_tags_*_v1.csv;
AP07 nutzt sie als Gegenprobe (D25, D26).
"""

import json
from datetime import datetime

import polars as pl

from sov import config
from sov.agreement import crosstab, kappa_ci, landis_koch
from sov.coding import CHECK_COLUMNS, build_check_sheet, read_sheet, write_sheet

N_CHECK = 40


def main() -> None:
    k1, k2 = config.LLM_CODERS
    a = read_sheet(config.CODING_DIR / "tags" / f"llm_tags_{k1}.csv")
    b = read_sheet(config.CODING_DIR / "tags" / f"llm_tags_{k2}.csv")
    df = a.join(b, on="tag", suffix=f"_{k2}").rename(
        {"kategorie": f"kategorie_{k1}", "begruendung": f"begruendung_{k1}"}
    )
    cats = list(config.TAG_CATEGORIES)
    ka = kappa_ci(df[f"kategorie_{k1}"].to_list(), df[f"kategorie_{k2}"].to_list(), cats)
    agree = df.filter(pl.col(f"kategorie_{k1}") == pl.col(f"kategorie_{k2}"))
    groups = {
        c: sorted(agree.filter(pl.col(f"kategorie_{k1}") == c)["tag"].to_list()) for c in ("G", "U")
    }
    meta = {
        "erzeugt": datetime.now().isoformat(timespec="seconds"),
        "kodierinstanzen": [config.LLM_MODELS[k1], config.LLM_MODELS[k2]],
        "kappa": round(ka["kappa"], 3),
        "n_tags": df.height,
        "n_einig": agree.height,
    }
    (config.PROCESSED_DIR / "groups.json").write_text(
        json.dumps({**groups, "_meta": meta}, indent=2, ensure_ascii=False)
    )

    ct = crosstab(df[f"kategorie_{k1}"].to_list(), df[f"kategorie_{k2}"].to_list(), cats, k1, k2)
    n_k = agree.filter(pl.col(f"kategorie_{k1}") == "K").height
    crit = "erfüllt" if ka["kappa"] >= config.KAPPA_MIN else "NICHT erfüllt"
    lines = [
        "# Einordnung der Tags – Übereinstimmung (AP05)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Kodierinstanzen: "
        f"{config.LLM_MODELS[k1]} und {config.LLM_MODELS[k2]} (AP16).",
        "",
        f"- Tags: {df.height}",
        f"- Cohens Kappa: **{ka['kappa']:.2f}** [{ka['ci_low']:.2f}; {ka['ci_high']:.2f}] "
        f"({landis_koch(ka['kappa'])}), Übereinstimmung {ka['uebereinstimmung']:.0%}",
        f"- Kriterium ≥ {config.KAPPA_MIN}: {crit}",
        f"- Gruppen (nur übereinstimmende Tags): Grundlagen {len(groups['G'])}, "
        f"Umgebung {len(groups['U'])}, beide K {n_k}",
        "",
        f"Kreuztabelle (Zeilen {k1}, Spalten {k2}):",
        "",
        "| | " + " | ".join(cats) + " |",
        "|---|" + "---|" * len(cats),
    ]
    for r in ct.to_dicts():
        lines.append(f"| {r[k1]} | " + " | ".join(str(r[c]) for c in cats) + " |")
    (config.RESULTS_DIR / "agreement_tags.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    wiki = pl.read_csv(config.PROCESSED_DIR / "tag_wiki.csv")
    pool = agree.join(wiki, on="tag").select(
        "tag", "wiki_auszug", pl.col(f"kategorie_{k1}").alias("kategorie"),
        pl.col(f"begruendung_{k1}").alias("begruendung"),
    )  # fmt: skip
    (config.CODING_DIR / "pruefung").mkdir(parents=True, exist_ok=True)
    write_sheet(
        build_check_sheet(pool, "tag", N_CHECK, config.SEED + 50),
        config.CODING_DIR / "pruefung" / "tags_40.csv",
        entry_cols=CHECK_COLUMNS,
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
