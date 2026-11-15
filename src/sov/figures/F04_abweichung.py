"""F04: Abweichung vom Trend 2023–2026 je Kennzahl in % (TF1, Pflicht).

Punkte = beobachtet / fortgeschrieben − 1. Grauer Balken = 95-%-Vorhersageintervall für 2024
(Hauptvergleichsjahr): Punkte außerhalb weichen stärker ab, als der Trend erklären kann.
"""

import matplotlib.pyplot as plt
import polars as pl
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

from sov import config
from sov.figures.common import SHORT
from sov.its import TF1_METRICS
from sov.plotting.style import COLORS, FULL, SEQUENTIAL, _de_number, apply_style, save_fig

NAME = "F04_abweichung"
YEAR_STYLE = {
    2023: {"color": SEQUENTIAL[3], "mfc": SEQUENTIAL[3]},
    2024: {"color": SEQUENTIAL[6], "mfc": SEQUENTIAL[6]},
    2025: {"color": SEQUENTIAL[5], "mfc": "white"},
    2026: {"color": SEQUENTIAL[6], "mfc": "white"},
}


def make() -> list[str]:
    apply_style()
    fit = pl.read_csv(config.PROCESSED_DIR / "its_fit.csv").filter(
        pl.col("population") == "klassisch"
    )
    metrics = list(TF1_METRICS)
    fig, ax = plt.subplots(figsize=FULL)
    for row, metric in enumerate(metrics):
        y = len(metrics) - 1 - row
        f = {r["year"]: r for r in fit.filter(pl.col("metric") == metric).to_dicts()}
        r24 = f[config.MAIN_POST_YEAR]
        lo = (r24["pi_low"] / r24["expected"] - 1) * 100
        hi = (r24["pi_high"] / r24["expected"] - 1) * 100
        ax.plot([lo, hi], [y, y], color=COLORS["trend_band"], lw=7, solid_capstyle="butt",
                zorder=1)  # fmt: skip
        ax.plot(
            [f[yr]["deviation_pct"] for yr in config.POST_YEARS], [y] * 4,
            color=COLORS["grid"], lw=0.8, zorder=2,
        )  # fmt: skip
        for yr in config.POST_YEARS:
            st = YEAR_STYLE[yr]
            ax.plot(
                f[yr]["deviation_pct"], y, marker="o", ms=5.5, ls="none", color=st["color"],
                mfc=st["mfc"], mew=1.3, zorder=3,
            )  # fmt: skip
    ax.axvline(0, color=COLORS["axis"], lw=1, zorder=0)
    ax.set_yticks(range(len(metrics)))
    ax.set_yticklabels([SHORT[m] for m in reversed(metrics)])
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlim(-105, 175)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{_de_number(v, 0)} %"))
    ax.set_xlabel("Abweichung vom fortgeschriebenen Trend 2015–2022")
    handles = [
        Line2D([], [], marker="o", ls="none", ms=5.5, color=YEAR_STYLE[yr]["color"],
               mfc=YEAR_STYLE[yr]["mfc"], mew=1.3, label=str(yr))
        for yr in config.POST_YEARS
    ]  # fmt: skip
    handles.append(Patch(color=COLORS["trend_band"], label="95-%-Intervall 2024"))
    ax.legend(
        handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=5, frameon=False,
        fontsize=7.5, handletextpad=0.3, columnspacing=1.2,
    )  # fmt: skip
    fig.tight_layout()
    return save_fig(fig, NAME)
