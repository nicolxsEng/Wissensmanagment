"""F08–F13: Gruppenvergleich Grundlagen gegen Umgebung (AP07, TF2).

F08 Index je Gruppe (Pflicht)         F09 Anteile in % mit „keine Gruppe“ (Anhang)
F10 Permutationstest (Pflicht)        F11 Behaltensquote je Tag (Pflicht)
F12 Vortrend gegen Behaltensquote     F13 Weglassen einzelner Tags, Gegenproben, Placebo (Anhang)
Hauptauswertung = Gruppen der zweiten Tag-Runde (D25); Gegenproben nach D26.
"""

import json

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from sov import config
from sov.figures.common import log_axis, num_axis, pct_axis, plot_observed, shade_pre_trend
from sov.groups import has_any
from sov.plotting.style import (
    COLORS,
    FULL,
    FULL_TALL,
    _de_number,
    add_chatgpt_marker,
    apply_style,
    label_line_end,
    save_fig,
    year_axis,
)

P = config.PROCESSED_DIR
GROUP_COLOR = {"G": COLORS["grundlagen"], "U": COLORS["umgebung"]}
GROUP_NAME = {"G": "Grundlagen", "U": "Umgebung"}
VARIANT_NAME = {
    "runde2": "Runde 2\n(Hauptauswertung)",
    "runde1": "Runde 1\n(Gegenprobe)",
    "kern": "Kern beider\nRunden",
}


def _index(variant: str = "runde2", population: str = "klassisch", mode: str = "beide"):
    gi = pl.read_csv(P / "group_index.csv")
    return gi.filter(
        (pl.col("variante") == variant)
        & (pl.col("population") == population)
        & (pl.col("zaehlung") == mode)
    ).sort("year")


def _de(x: float, d: int = 1, sign: bool = False) -> str:
    s = _de_number(x, d)
    return ("+" + s) if sign and x > 0 else s


# ----------------------------------------------------------------------------- F08
def make_f08() -> list[str]:
    apply_style()
    gi = _index()
    fig, ax = plt.subplots(figsize=FULL)
    shade_pre_trend(ax)
    ax.axhline(100, color=COLORS["axis"], lw=0.8, zorder=1)
    for g in ("G", "U"):
        s = gi.filter(pl.col("gruppe") == g)
        plot_observed(ax, s["year"].to_list(), s["index"].to_list(), GROUP_COLOR[g])
        last = s.row(-1, named=True)
        label_line_end(ax, last["year"], last["index"], GROUP_NAME[g], GROUP_COLOR[g])
        r24 = s.filter(pl.col("year") == config.MAIN_POST_YEAR).row(0, named=True)
        ax.annotate(
            _de(r24["index"]),
            (r24["year"], r24["index"]),
            xytext=(0, 7 if g == "U" else -8),
            textcoords="offset points",
            ha="center",
            va="bottom" if g == "U" else "top",
            fontsize=7.5,
            color=GROUP_COLOR[g],
        )
    num_axis(ax)
    ax.set_ylim(0, 150)
    ax.set_ylabel(f"Anteil an allen Fragen, Index ({config.BASE_YEAR} = 100)")
    year_axis(ax, 2008, 2026, 2)
    ax.set_xlim(2007.5, 2027.8)
    add_chatgpt_marker(ax, where="bottom")
    ax.annotate(
        "vor dem Trendzeitraum",
        xy=(2011, 1),
        xycoords=("data", "axes fraction"),
        xytext=(0, -2),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=7,
        color=COLORS["ink2"],
    )
    fig.tight_layout()
    return save_fig(fig, "F08_index_gruppen")


# ----------------------------------------------------------------------------- F09
def make_f09() -> list[str]:
    from sov.io import load_questions

    apply_style()
    groups = json.loads((P / "groups.json").read_text())
    q = load_questions(["year", "tags", "is_classic"]).filter("is_classic")
    none = (
        q.group_by("year")
        .agg(share=(~(has_any(groups["G"]) | has_any(groups["U"]))).mean())
        .sort("year")
    )
    gi = _index()
    fig, ax = plt.subplots(figsize=FULL)
    shade_pre_trend(ax)
    series = [
        ("G", gi.filter(pl.col("gruppe") == "G"), GROUP_COLOR["G"], "Grundlagen"),
        ("U", gi.filter(pl.col("gruppe") == "U"), GROUP_COLOR["U"], "Umgebung"),
        ("K", none, COLORS["sonstige"], "keine Gruppe"),
    ]
    for _k, s, color, name in series:
        plot_observed(ax, s["year"].to_list(), s["share"].to_list(), color, scale=100)
        last = s.row(-1, named=True)
        label_line_end(ax, last["year"], 100 * last["share"], name, color)
    pct_axis(ax)
    ax.set_ylim(0, 70)
    ax.set_ylabel("Anteil an allen Fragen")
    year_axis(ax, 2008, 2026, 2)
    ax.set_xlim(2007.5, 2028.3)
    add_chatgpt_marker(ax)
    fig.tight_layout()
    return save_fig(fig, "F09_anteile_gruppen")


# ----------------------------------------------------------------------------- F10
def make_f10() -> list[str]:
    apply_style()
    draws = pl.read_parquet(P / "permutation_draws.parquet").filter(pl.col("variante") == "runde2")
    perm = pl.read_csv(P / "permutation.csv").filter(pl.col("variante") == "runde2")
    fig, axes = plt.subplots(2, 2, figsize=FULL_TALL)
    for ax, y in zip(axes.flat, config.POST_YEARS, strict=True):
        d = draws.filter(pl.col("year") == y)["abstand"].to_numpy()
        d = d[np.isfinite(d)]
        r = perm.filter(pl.col("year") == y).row(0, named=True)
        lo, hi = np.quantile(d, [0.001, 0.999])
        lo, hi = min(lo, r["beobachtet"]), max(hi, r["beobachtet"])
        bins = np.linspace(lo, hi, 60)
        ax.hist(np.clip(d, lo, hi), bins=bins, color=COLORS["trend_band"], lw=0, zorder=2)
        ax.axvline(r["q95_zufall"], color=COLORS["ink2"], lw=0.8, ls=(0, (2, 2)), zorder=3)
        ax.axvline(r["beobachtet"], color=COLORS["umgebung"], lw=1.8, zorder=4)
        ax.annotate(
            f"beobachtet {_de(r['beobachtet'], sign=True)}\np = {_de_number(r['p'], 3)}",
            xy=(r["beobachtet"], 1),
            xycoords=("data", "axes fraction"),
            xytext=(-4, -2),
            textcoords="offset points",
            ha="right",
            va="top",
            fontsize=7.5,
            color=COLORS["umgebung"],
            bbox={"fc": "white", "ec": "none", "pad": 1.0},
            zorder=5,
        )
        ax.set_title(
            f"Oktober {y}" + (" (nur Bestätigung)" if y in config.CONFIRM_YEARS else ""),
            loc="left",
            fontsize=8.5,
            color=COLORS["gesamt"],
        )
        ax.set_yticks([])
        ax.grid(False)
        ax.spines["left"].set_visible(False)
        ax.xaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _p: ("+" if v > 0 else "") + _de_number(v, 0))
        )
    axes[0, 0].annotate(
        "95 % der Zufallsgruppen\nliegen links davon",
        xy=(perm.filter(pl.col("year") == 2023)["q95_zufall"].item(), 0.55),
        xycoords=("data", "axes fraction"),
        xytext=(-4, 0),
        textcoords="offset points",
        ha="right",
        fontsize=7,
        color=COLORS["ink2"],
    )
    fig.supxlabel(
        "Abstand Index Umgebung − Index Grundlagen (10.000 Zufallsgruppen gleicher Größe)",
        fontsize=8.5,
        color=COLORS["ink2"],
    )
    fig.tight_layout(h_pad=1.6, w_pad=2)
    return save_fig(fig, "F10_permutation")


# ----------------------------------------------------------------------------- F11
def make_f11() -> list[str]:
    apply_style()
    ts = pl.read_csv(P / "tag_shift.csv").filter(pl.col("gruppe_runde2").is_in(["G", "U"]))
    ts = ts.sort("behalten").with_row_index("rang", offset=1)
    fig, ax = plt.subplots(figsize=FULL)
    ax.axhline(1, color=COLORS["ink2"], lw=0.8, zorder=1)
    for g in ("G", "U"):
        s = ts.filter(pl.col("gruppe_runde2") == g)
        med = _de_number(s["behalten"].median(), 2)
        ax.scatter(
            s["rang"],
            s["behalten"],
            s=14 if g == "U" else 8,
            color=GROUP_COLOR[g],
            lw=0,
            zorder=3 if g == "U" else 2,
            label=f"{GROUP_NAME[g]} ({s.height} Tags, Median {med})",
        )
    offsets = {"azure": (-4, 4, "right"), "docker": (0, 6, "center"),
               "heroku": (5, -9, "left"), ".net-6.0": (5, -9, "left")}  # fmt: skip
    for t, (dx, dy, ha) in offsets.items():
        r = ts.filter(pl.col("tag") == t)
        if r.height:
            r = r.row(0, named=True)
            ax.annotate(
                t,
                (r["rang"], r["behalten"]),
                xytext=(dx, dy),
                textcoords="offset points",
                ha=ha,
                fontsize=6.5,
                color=GROUP_COLOR[r["gruppe_runde2"]],
            )
    log_axis(ax, [0.1, 0.2, 0.5, 1, 2, 5], decimals=1)
    lo = max(0.05, ts["behalten"].filter(ts["behalten"] > 0).min() * 0.8)
    ax.set_ylim(lo, ts["behalten"].max() * 1.4)
    ax.set_xlim(0, ts.height + 1)
    ax.set_xticks([])
    ax.set_xlabel("Tags, sortiert nach Behaltensquote")
    ax.set_ylabel(f"Anteil {config.MAIN_POST_YEAR} / Anteil {config.BASE_YEAR} (Log-Skala)")
    ax.annotate(
        "1 = so stark geschrumpft wie Stack Overflow insgesamt",
        xy=(0.01, 1),
        xycoords=("axes fraction", "data"),
        xytext=(0, 3),
        textcoords="offset points",
        fontsize=7,
        color=COLORS["ink2"],
    )
    ax.legend(loc="lower right", markerscale=1.4)
    fig.tight_layout()
    return save_fig(fig, "F11_behalten")


# ----------------------------------------------------------------------------- F12
def make_f12() -> list[str]:
    apply_style()
    ts = pl.read_csv(P / "tag_shift.csv").filter(
        pl.col("gruppe_runde2").is_in(["G", "U"])
        & pl.col("vortrend").is_finite()
        & (pl.col("behalten") > 0)
        & (pl.col("vortrend") > 0)
    )
    fig, ax = plt.subplots(figsize=(FULL[0] * 0.7, FULL[1] * 1.2))
    ax.axhline(1, color=COLORS["axis"], lw=0.8, zorder=1)
    ax.axvline(1, color=COLORS["axis"], lw=0.8, zorder=1)
    for g in ("G", "U"):
        s = ts.filter(pl.col("gruppe_runde2") == g)
        ax.scatter(
            s["vortrend"],
            s["behalten"],
            s=16 if g == "U" else 10,
            color=GROUP_COLOR[g],
            alpha=0.85,
            lw=0,
            zorder=3 if g == "U" else 2,
            label=GROUP_NAME[g],
        )
    log_axis(ax, [0.2, 0.5, 1, 2, 5], decimals=1)
    log_axis(ax, [0.5, 1, 2, 5, 10, 30], decimals=1, axis="x")
    ax.grid(True, axis="both")
    ax.set_xlabel("Vortrend: Anteil 2022 / Anteil 2019 (Log-Skala)")
    ax.set_ylabel("Behalten: Anteil 2024 / Anteil 2022 (Log-Skala)")
    ax.legend(loc="center right")
    rho = np.corrcoef(np.log(ts["vortrend"]), np.log(ts["behalten"]))[0, 1]
    ax.annotate(
        f"Korrelation (log): {_de_number(rho, 2)}",
        xy=(0.98, 0.03),
        xycoords="axes fraction",
        ha="right",
        fontsize=7,
        color=COLORS["ink2"],
    )
    fig.tight_layout()
    return save_fig(fig, "F12_vortrend")


# ----------------------------------------------------------------------------- F13
def make_f13() -> list[str]:
    apply_style()
    loo = pl.read_csv(P / "leave_one_out.csv")
    placebo = pl.read_csv(P / "placebo.csv")
    variants = list(VARIANT_NAME)
    fig, (a1, a2) = plt.subplots(
        1, 2, figsize=FULL_TALL[:1] + (8.5 / 2.54,), gridspec_kw={"width_ratios": [3, 2]}
    )
    ys = np.arange(len(variants))[::-1]
    marks = [
        ("klassisch", "beide", "o", "Hauptrechnung", COLORS["gesamt"]),
        ("klassisch", "nur_eine", "s", "nur Fragen einer Gruppe", COLORS["ink2"]),
        ("score_ge_1", "beide", "D", "nur Fragen mit Score ≥ 1", COLORS["drittes"]),
    ]
    for y, v in zip(ys, variants, strict=True):
        d = loo.filter(pl.col("variante") == v)["abstand"]
        a1.plot([d.min(), d.max()], [y, y], color=COLORS["trend_band"], lw=6,
                solid_capstyle="butt", zorder=1)  # fmt: skip
        for k, (pop, mode, m, name, c) in enumerate(marks):
            s = _index(v, pop, mode)
            val = (
                s.filter((pl.col("gruppe") == "U") & (pl.col("year") == config.MAIN_POST_YEAR))[
                    "index"
                ].item()
                - s.filter((pl.col("gruppe") == "G") & (pl.col("year") == config.MAIN_POST_YEAR))[
                    "index"
                ].item()
            )
            a1.plot(val, y + (0, 0.25, -0.25)[k], marker=m, ms=4.5, color=c, ls="none", zorder=3,
                    label=name if y == ys[0] else None)  # fmt: skip
    a1.axvline(0, color=COLORS["ink2"], lw=0.8)
    a1.set_yticks(ys, [VARIANT_NAME[v] for v in variants])
    a1.set_xlabel(f"Abstand {config.MAIN_POST_YEAR} (Index U − Index G)")
    a1.set_title(
        "Gegenproben; grauer Balken = Spanne beim\nWeglassen jeweils eines Tags",
        loc="left",
        fontsize=8.5,
        color=COLORS["gesamt"],
    )
    a1.grid(True, axis="x")
    a1.grid(False, axis="y")
    for y, v in zip(ys, variants, strict=True):
        r = placebo.filter(pl.col("variante") == v).row(0, named=True)
        a2.plot([r["median_zufall"], r["q95_zufall"]], [y, y], color=COLORS["trend_band"],
                lw=6, solid_capstyle="butt", zorder=1)  # fmt: skip
        a2.plot(r["beobachtet"], y, marker="o", ms=4.5, color=COLORS["gesamt"], zorder=3)
    a2.axvline(0, color=COLORS["ink2"], lw=0.8)
    a2.set_yticks(ys, [""] * len(ys))
    a2.set_xlabel(f"Abstand {config.PLACEBO_COMPARE_YEAR} (Basis {config.PLACEBO_BASE_YEAR} = 100)")
    a2.set_title(
        "Placebo vor ChatGPT; Balken = Median bis\n95 % der Zufallsgruppen",
        loc="left",
        fontsize=8.5,
        color=COLORS["gesamt"],
    )
    a2.grid(True, axis="x")
    a2.grid(False, axis="y")
    lim = max(abs(loo["abstand"].min()), loo["abstand"].max()) * 1.1
    a1.set_xlim(-10, lim)
    a2.set_xlim(-30, 40)
    for a in (a1, a2):
        a.set_ylim(-0.6, len(variants) - 0.4)
    fig.legend(*a1.get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=7.5,
               bbox_to_anchor=(0.5, -0.02))  # fmt: skip
    fig.tight_layout(w_pad=2, rect=(0, 0.07, 1, 1))
    return save_fig(fig, "F13_robustheit")
