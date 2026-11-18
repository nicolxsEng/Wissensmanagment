"""F14–F15: automatische Einordnung der Fragetexte (AP10, TF2 ohne Tags).

F14 Textbasierte Anteile G/U/S je Jahr mit Wilson-Intervall und korrigierten Anteilen;
    daneben Index aus Tags (Runde 2) und aus Texten im Vergleich (Pflicht)
F15 Güte der Verfahren: Macro-F1 je Kandidat mit Bootstrap-KI; Konfusionsmatrix des
    Gewinners (Anhang)
"""

import json

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

from sov import config
from sov.figures.common import num_axis, pct_axis, plot_observed
from sov.plotting.style import (
    COLORS,
    FULL,
    SEQUENTIAL,
    _de_number,
    add_chatgpt_marker,
    apply_style,
    save_fig,
    year_axis,
)

P = config.PROCESSED_DIR
C = config.RESULTS_DIR / "classify"
LABEL_COLOR = {"G": COLORS["grundlagen"], "U": COLORS["umgebung"], "S": COLORS["sonstige"]}
LABEL_NAME = {"G": "Grundlagen", "U": "Umgebung", "S": "Sonstige"}
CANDIDATE_NAME = {
    "setfit": "SetFit",
    "tfidf_logreg": "TF-IDF + log. Regression",
    "zero_shot": "Zero-Shot (ohne Training)",
}


# ----------------------------------------------------------------------------- F14
def make_f14() -> list[str]:
    apply_style()
    raw = pl.read_csv(P / "text_group_shares.csv").sort("year")
    adj = pl.read_csv(P / "text_group_shares_adjusted.csv").sort("year")
    gi = (
        pl.read_csv(P / "group_index.csv")
        .filter(
            (pl.col("variante") == "runde2")
            & (pl.col("population") == "klassisch")
            & (pl.col("zaehlung") == "beide")
            & (pl.col("year") >= config.TREND_START)
        )
        .sort("year")
    )
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FULL[0], 8.2 / 2.54))

    # links: Anteile aus dem Text
    for lab in ("G", "U", "S"):
        s = raw.filter(pl.col("label") == lab)
        yrs = s["year"].to_list()
        a1.fill_between(yrs, s["ci_low"] * 100, s["ci_high"] * 100, color=LABEL_COLOR[lab],
                        alpha=0.18, lw=0, zorder=1)  # fmt: skip
        plot_observed(a1, yrs, s["share"].to_list(), LABEL_COLOR[lab], scale=100, ms=2.8, lw=1.5)
        k = adj.filter(pl.col("label") == lab)
        a1.plot(k["year"], k["share_adjusted"] * 100, color=LABEL_COLOR[lab], lw=0.9,
                ls=(0, (3, 2)), zorder=2)  # fmt: skip
        r = s.filter(pl.col("year") == 2018).row(0, named=True)
        a1.annotate(
            LABEL_NAME[lab],
            (2018, r["share"] * 100),
            xytext=(0, {"G": 9, "U": 6, "S": 14}[lab]),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.5,
            color=LABEL_COLOR[lab],
        )
    a1.set_ylim(0, 90)
    pct_axis(a1)
    a1.set_ylabel("Anteil der Fragen")
    a1.set_title("Einordnung der Fragetexte (SetFit)", loc="left", fontsize=8.5,
                 color=COLORS["gesamt"])  # fmt: skip
    a1.legend(
        handles=[
            Line2D(
                [],
                [],
                color=COLORS["ink2"],
                lw=1.5,
                marker="o",
                ms=2.8,
                label="roh, Band = 95-%-KI",
            ),  # fmt: skip
            Line2D(
                [],
                [],
                color=COLORS["ink2"],
                lw=0.9,
                ls=(0, (3, 2)),
                label="korrigiert (Konfusionsmatrix)",
            ),  # fmt: skip
        ],
        loc="center left",
        bbox_to_anchor=(0, 0.55),
        fontsize=7,
        frameon=False,
    )

    # rechts: Index 2022 = 100, Tags gegen Text
    a2.axhline(100, color=COLORS["axis"], lw=0.8, zorder=1)
    base = {lab: raw.filter((pl.col("label") == lab) & (pl.col("year") == config.BASE_YEAR))[
        "share"].item() for lab in ("G", "U")}  # fmt: skip
    for g in ("G", "U"):
        t = gi.filter(pl.col("gruppe") == g)
        plot_observed(a2, t["year"].to_list(), t["index"].to_list(), LABEL_COLOR[g],
                      ms=2.8, lw=1.5)  # fmt: skip
        x = raw.filter(pl.col("label") == g)
        a2.plot(x["year"], x["share"] / base[g] * 100, color=LABEL_COLOR[g], lw=1.1,
                ls=(0, (1, 1.2)), marker="s", ms=2.4, mfc="white", mew=0.9, zorder=2)  # fmt: skip
        a2.annotate(
            LABEL_NAME[g],
            (2016, t.filter(pl.col("year") == 2016)["index"].item()),
            xytext=(0, 7 if g == "G" else -9),
            textcoords="offset points",
            ha="center",
            va="bottom" if g == "G" else "top",
            fontsize=7.5,
            color=LABEL_COLOR[g],
        )
    a2.set_ylim(0, 200)
    num_axis(a2)
    a2.set_ylabel(f"Index ({config.BASE_YEAR} = 100)")
    a2.set_title("Index aus Tags und aus Texten", loc="left", fontsize=8.5,
                 color=COLORS["gesamt"])  # fmt: skip
    a2.legend(
        handles=[
            Line2D(
                [], [], color=COLORS["ink2"], lw=1.5, marker="o", ms=2.8, label="Tags (Runde 2)"
            ),  # fmt: skip
            Line2D(
                [],
                [],
                color=COLORS["ink2"],
                lw=1.1,
                ls=(0, (1, 1.2)),
                marker="s",
                ms=2.4,
                mfc="white",
                label="Texte (SetFit)",
            ),  # fmt: skip
        ],
        loc="upper left",
        fontsize=7,
        frameon=False,
    )
    for i, ax in enumerate((a1, a2)):
        year_axis(ax, config.TREND_START, 2026, 2)
        add_chatgpt_marker(ax, label=(i == 0), where="top")
    fig.tight_layout(w_pad=2)
    return save_fig(fig, "F14_text_anteile")


# ----------------------------------------------------------------------------- F15
def make_f15() -> list[str]:
    apply_style()
    res = pl.read_csv(C / "vergleich.csv").sort("macro_f1")
    conf = json.loads((C / "konfusion.json").read_text())
    best = json.loads((C / "modell.json").read_text())["verfahren"]
    fig, (a1, a2) = plt.subplots(
        1, 2, figsize=(FULL[0], 6.5 / 2.54), gridspec_kw={"width_ratios": [3, 2]}
    )

    # links: Macro-F1 mit KI
    ys = np.arange(res.height)
    for y, r in zip(ys, res.to_dicts(), strict=True):
        c = COLORS["gesamt"] if r["kandidat"] == best else COLORS["ink2"]
        a1.plot([r["ci_low"], r["ci_high"]], [y, y], color=COLORS["trend_band"], lw=5,
                solid_capstyle="butt", zorder=1)  # fmt: skip
        a1.plot(r["macro_f1"], y, "o", ms=5, color=c, zorder=3)
        a1.annotate(_de_number(r["macro_f1"], 2), (r["macro_f1"], y), xytext=(0, 6),
                    textcoords="offset points", ha="center", fontsize=7.5, color=c)  # fmt: skip
    a1.axvline(config.MACRO_F1_MIN, color=COLORS["umgebung"], lw=0.9, ls=(0, (3, 2)), zorder=2)
    a1.annotate(
        f"Kriterium {_de_number(config.MACRO_F1_MIN, 2)}",
        xy=(config.MACRO_F1_MIN, 0),
        xycoords=("data", "axes fraction"),
        xytext=(3, 2),
        textcoords="offset points",
        fontsize=7,
        color=COLORS["umgebung"],
    )
    a1.set_yticks(ys, [CANDIDATE_NAME.get(k, k) for k in res["kandidat"]])
    a1.set_ylim(-0.6, res.height - 0.4)
    a1.set_xlim(0, 1)
    a1.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: _de_number(v, 1)))
    a1.set_xlabel(f"Macro-F1 auf {res['n'][0]} Testfragen (Band = 95-%-KI)")
    a1.grid(True, axis="x")
    a1.grid(False, axis="y")

    # rechts: Konfusionsmatrix, Farbe = Anteil der Zeile
    m = np.asarray(conf[best], dtype=float)
    rowp = m / m.sum(axis=1, keepdims=True)
    cmap = LinearSegmentedColormap.from_list("seq", ["#ffffff", *SEQUENTIAL])
    a2.imshow(rowp, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    labs = list(LABEL_NAME)
    for i in range(3):
        for j in range(3):
            a2.text(j, i, f"{int(m[i, j])}", ha="center", va="center", fontsize=8,
                    color="white" if rowp[i, j] > 0.55 else COLORS["gesamt"])  # fmt: skip
    a2.set_xticks(range(3), labs)
    a2.set_yticks(range(3), [f"{lab} ({int(m[i].sum())})" for i, lab in enumerate(labs)])
    a2.set_xlabel("vorhergesagt")
    a2.set_ylabel("Referenz (Konsens)")
    a2.set_title(f"Konfusionsmatrix {CANDIDATE_NAME.get(best, best)}", loc="left", fontsize=8.5,
                 color=COLORS["gesamt"])  # fmt: skip
    a2.grid(False)
    for sp in a2.spines.values():
        sp.set_visible(False)
    a2.tick_params(length=0)
    fig.tight_layout(w_pad=2.5)
    return save_fig(fig, "F15_klassifikation_guete")
