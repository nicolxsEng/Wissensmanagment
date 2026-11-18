"""AP07: Gruppenvergleich Grundlagen (G) gegen Umgebung (U) über Tags, mit Gegenproben.

uv run python scripts/07_groups.py

Gruppenvarianten (D25, D26):
  runde2  Hauptauswertung, data/processed/groups.json (Prompt v3, vorab festgelegt)
  runde1  Gegenprobe, data/processed/groups_v1.json
  kern    Gegenprobe, Tags, die in beiden Runden in derselben Gruppe sind
  mensch  Gegenprobe, nur von den Autor:innen blind bestätigte Tags (D29;
          data/processed/groups_mensch.json aus `scripts/17_pruefung.py auswerten`, falls vorhanden)
Populationen: klassisch (Hauptauswertung), score_ge_1; Zählweise: beide (D07), nur_eine.

Ausgaben (data/processed/): group_index.csv, permutation.csv, permutation_draws.parquet,
leave_one_out.csv, placebo.csv, tag_shift.csv, its_groups.csv; Bericht results/groups.md
"""

import json
import time
from datetime import datetime

import polars as pl

from sov import config
from sov.groups import (
    TagMatrix,
    distance,
    group_shares,
    index_distance,
    leave_one_out,
    permutation_summary,
    random_group_shares,
    tag_shift,
)
from sov.io import load_questions
from sov.its import fit_pretrend, segmented

P = config.PROCESSED_DIR
BASE, POST = config.BASE_YEAR, config.MAIN_POST_YEAR
PB, PC = config.PLACEBO_BASE_YEAR, config.PLACEBO_COMPARE_YEAR


def vt(x: float) -> str:
    """Vortrend; unendlich, wenn es den Tag 2019 noch nicht gab."""
    return de(x, 2) if x != float("inf") else "– (2019 noch nicht vorhanden)"


def de(x: float, d: int = 1, sign: bool = False) -> str:
    s = f"{x:+,.{d}f}" if sign else f"{x:,.{d}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def load_variants() -> dict[str, dict[str, list[str]]]:
    r2 = json.loads((P / "groups.json").read_text())
    r1 = json.loads((P / "groups_v1.json").read_text())
    kern = {g: sorted(set(r2[g]) & set(r1[g])) for g in ("G", "U")}
    out = {"runde2": {g: r2[g] for g in "GU"}, "runde1": {g: r1[g] for g in "GU"}, "kern": kern}
    if (P / "groups_mensch.json").exists():
        hm = json.loads((P / "groups_mensch.json").read_text())
        out["mensch"] = {g: hm[g] for g in "GU"}
    return out


def main() -> None:
    t0 = time.perf_counter()
    variants = load_variants()
    cand = pl.read_csv(P / "tag_wiki.csv")["tag"].to_list()
    q = load_questions(["year", "tags", "is_classic", "score"]).filter("is_classic")
    pops = {"klassisch": q, "score_ge_1": q.filter(pl.col("score") >= 1)}

    # 1. Anteile und Index
    idx = []
    for v, groups in variants.items():
        for pop, qq in pops.items():
            for mode in ("beide", "nur_eine"):
                s = group_shares(qq, groups, exclusive=mode == "nur_eine")
                idx.append(
                    s.with_columns(
                        variante=pl.lit(v), population=pl.lit(pop), zaehlung=pl.lit(mode)
                    )
                )
    gi = pl.concat(idx).select(
        "variante",
        "population",
        "zaehlung",
        "year",
        "gruppe",
        "n_group",
        "n_total",
        "share",
        "index",
    )
    gi.write_csv(P / "group_index.csv")

    # 2.–4. Permutation, Weglassen, Placebo (klassisch, beide)
    tm = TagMatrix(q, cand, [PB, PC, BASE, *config.POST_YEARS])
    perm_rows, placebo_rows, loo, draws = [], [], [], []
    for v, groups in variants.items():
        g, u = groups["G"], groups["U"]
        obs = tm.shares(tm.indicator([g, u]))
        sg, su = random_group_shares(tm, len(g), len(u), seed=config.SEED + 70)
        for y in config.POST_YEARS:
            d_obs = float(index_distance(tm, obs[:, [0]], obs[:, [1]], y, BASE)[0])
            rnd = index_distance(tm, sg, su, y, BASE)
            perm_rows.append(
                {"variante": v, "year": y, "n_g": len(g), "n_u": len(u)}
                | permutation_summary(d_obs, rnd)
            )
            draws.append(pl.DataFrame({"variante": v, "year": y, "abstand": rnd}))
        d_pl = float(index_distance(tm, obs[:, [0]], obs[:, [1]], PC, PB)[0])
        placebo_rows.append(
            {"variante": v, "basis": PB, "vergleich": PC}
            | permutation_summary(d_pl, index_distance(tm, sg, su, PC, PB))
        )
        loo.append(leave_one_out(tm, g, u, POST, BASE).with_columns(variante=pl.lit(v)))
    perm = pl.DataFrame(perm_rows)
    perm.write_csv(P / "permutation.csv")
    pl.concat(draws).write_parquet(P / "permutation_draws.parquet")
    placebo = pl.DataFrame(placebo_rows)
    placebo.write_csv(P / "placebo.csv")
    loo_df = pl.concat(loo).select("variante", "gruppe", "ohne_tag", "abstand")
    loo_df.write_csv(P / "leave_one_out.csv")

    # 5. Behaltensquote je Tag
    lab = {
        v: {t: gname for gname, ts in groups.items() for t in ts} for v, groups in variants.items()
    }
    ts = tag_shift(q, cand).with_columns(
        [pl.col("tag").replace_strict(lab[v], default="").alias(f"gruppe_{v}") for v in variants]
    )
    ts.write_csv(P / "tag_shift.csv")

    # Unterbrochene Zeitreihe der Gruppenanteile (AP08 für TF2)
    its = []
    for v in variants:
        for gname in ("G", "U"):
            s = gi.filter(
                (pl.col("variante") == v)
                & (pl.col("population") == "klassisch")
                & (pl.col("zaehlung") == "beide")
                & (pl.col("gruppe") == gname)
            ).sort("year")
            yrs, vals = s["year"].to_list(), s["share"].to_list()
            base = {"variante": v, "gruppe": gname}
            its += [base | {"art": "fortschreibung"} | r for r in fit_pretrend(yrs, vals, "logit")]
            its += [base | {"art": "segmentiert"} | r for r in segmented(yrs, vals, "logit")]
    pl.DataFrame(its, infer_schema_length=None).write_csv(P / "its_groups.csv")

    report(variants, gi, perm, placebo, loo_df, ts, its, time.perf_counter() - t0)


def report(variants, gi, perm, placebo, loo, ts, its, secs) -> None:
    def sel(v, pop="klassisch", mode="beide"):
        return gi.filter(
            (pl.col("variante") == v) & (pl.col("population") == pop) & (pl.col("zaehlung") == mode)
        )

    def ix(s, gname, y):
        return s.filter((pl.col("gruppe") == gname) & (pl.col("year") == y))["index"].item()

    names = {
        "runde2": "Runde 2 (Hauptauswertung)",
        "runde1": "Runde 1 (Gegenprobe)",
        "kern": "Kern beider Runden (Gegenprobe)",
        "mensch": "von Menschen bestätigt (Gegenprobe, D29)",
    }
    L = [
        "# Gruppenvergleich Grundlagen gegen Umgebung (AP07)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M} ({secs:.0f} s). Klassische Fragen, Synonyme "
        "zusammengeführt. Anteil = Fragen mit ≥ 1 Tag der Gruppe / alle Fragen des Oktobers; "
        f"Index {BASE} = 100; Abstand = Index U − Index G. Gruppen: nur Tags, die beide Modelle "
        "gleich einordneten (D25, D26).",
        "",
        "## Index je Gruppe",
        "",
        "| Variante | Tags G / U | G 2023 | G 2024 | U 2023 | U 2024 | Abstand 2024 | "
        "Abstand 2025 | Abstand 2026 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for v, groups in variants.items():
        s = sel(v)
        L.append(
            f"| {names[v]} | {len(groups['G'])} / {len(groups['U'])} | "
            f"{de(ix(s, 'G', 2023))} | {de(ix(s, 'G', POST))} | {de(ix(s, 'U', 2023))} | "
            f"{de(ix(s, 'U', POST))} | **{de(distance(s, POST), sign=True)}** | "
            f"{de(distance(s, 2025), sign=True)} | {de(distance(s, 2026), sign=True)} |"
        )
    L += [
        "",
        "Gegenproben zur Zählweise und Population (Abstand 2024):",
        "",
        "| Variante | klassisch, beide | klassisch, nur eine Gruppe | Score ≥ 1, beide |",
        "|---|---|---|---|",
    ]
    for v in variants:
        L.append(
            f"| {names[v]} | {de(distance(sel(v), POST), sign=True)} | "
            f"{de(distance(sel(v, mode='nur_eine'), POST), sign=True)} | "
            f"{de(distance(sel(v, pop='score_ge_1'), POST), sign=True)} |"
        )
    L += ["", "Anteile (in %) in der Hauptauswertung:", "", "| Jahr | G | U |", "|---|---|---|"]
    s = sel("runde2")
    for y in sorted(set(s["year"].to_list())):
        if y >= config.TREND_START:
            sh = {r["gruppe"]: r["share"] for r in s.filter(pl.col("year") == y).to_dicts()}
            L.append(f"| {y} | {de(100 * sh['G'])} | {de(100 * sh['U'])} |")
    L += [
        "",
        f"## Permutationstest ({config.N_PERMUTATIONS:,} Zufallsgruppen gleicher Größe aus "
        "den 269 Kandidaten-Tags; einseitig)".replace(",", "."),
        "",
        "| Variante | Jahr | beobachtet | Median Zufall | 95 % Zufall | max. Zufall | "
        "Perzentil | p |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in perm.to_dicts():
        L.append(
            f"| {names[r['variante']]} | {r['year']} | {de(r['beobachtet'], sign=True)} | "
            f"{de(r['median_zufall'], sign=True)} | {de(r['q95_zufall'], sign=True)} | "
            f"{de(r['max_zufall'], sign=True)} | {de(r['perzentil'])} | {de(r['p'], 4)} |"
        )
    L += [
        "",
        f"## Placebo-Test (Basis {PB} = 100, Vergleich {PC}, beide vor ChatGPT)",
        "",
        "| Variante | Abstand | Perzentil unter Zufallsgruppen | p |",
        "|---|---|---|---|",
    ]
    for r in placebo.to_dicts():
        L.append(
            f"| {names[r['variante']]} | {de(r['beobachtet'], sign=True)} | "
            f"{de(r['perzentil'])} | {de(r['p'], 4)} |"
        )
    L += [
        "",
        f"## Weglassen einzelner Tags (Abstand {POST})",
        "",
        "| Variante | kleinster Abstand (ohne) | größter Abstand (ohne) |",
        "|---|---|---|",
    ]
    for v in variants:
        d = loo.filter(pl.col("variante") == v).sort("abstand")
        lo, hi = d.row(0, named=True), d.row(-1, named=True)
        L.append(
            f"| {names[v]} | {de(lo['abstand'], sign=True)} ({lo['ohne_tag']}) | "
            f"{de(hi['abstand'], sign=True)} ({hi['ohne_tag']}) |"
        )
    L += [
        "",
        f"## Behaltensquote je Tag (Anteil {POST} / Anteil {BASE}; 1 = wie Stack Overflow "
        "insgesamt), Hauptauswertung",
        "",
        "| Gruppe | Tags | Median Behalten | Anteil Tags > 1 | Median Vortrend 2019→2022 |",
        "|---|---|---|---|---|",
    ]
    for gname in ("G", "U"):
        t = ts.filter(pl.col("gruppe_runde2") == gname)
        L.append(
            f"| {gname} | {t.height} | {de(t['behalten'].median(), 2)} | "
            f"{de(100 * (t['behalten'] > 1).mean(), 0)} % | {de(t['vortrend'].median(), 2)} |"
        )
    L += [
        "",
        "Umgebungs-Tags (Hauptauswertung):",
        "",
        "| Tag | Fragen 2022 | Fragen 2024 | Behalten | Vortrend |",
        "|---|---|---|---|---|",
    ]
    for r in ts.filter(pl.col("gruppe_runde2") == "U").sort("behalten").to_dicts():
        L.append(
            f"| {r['tag']} | {de(r['n_2022'], 0)} | {de(r['n_2024'], 0)} | "
            f"{de(r['behalten'], 2)} | {vt(r['vortrend'])} |"
        )
    L += [
        "",
        "## Abweichung vom Trend 2015–2022 (Logit-Skala, Hauptauswertung)",
        "",
        "| Gruppe | 2023 | 2024 | 2025 | 2026 |",
        "|---|---|---|---|---|",
    ]
    for gname in ("G", "U"):
        rows = {
            r["year"]: r
            for r in its
            if r["variante"] == "runde2" and r["gruppe"] == gname and r["art"] == "fortschreibung"
        }

        def cell(y, rows=rows):
            r = rows[y]
            m = {"darunter": " ▼", "darüber": " ▲"}.get(r["outside_pi"], "")
            return f"{de(r['deviation_pct'], 0, sign=True)} %{m}"

        L.append(f"| {gname} | " + " | ".join(cell(y) for y in config.POST_YEARS) + " |")
    L += ["", "▼ / ▲ = außerhalb des 95-%-Vorhersageintervalls. 2025/2026 nur Bestätigung."]
    (config.RESULTS_DIR / "groups.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
