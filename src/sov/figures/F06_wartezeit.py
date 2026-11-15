"""F06: Anteil der Fragen mit erster Antwort innerhalb von x Stunden (TF1, Pflicht).

Kurven je Oktober über alle klassischen Fragen; sie enden bei 7 Tagen auf dem Anteil der
beantworteten Fragen. Vor ChatGPT grau, danach blau (heller = früher).
"""

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

from sov import config
from sov.figures.common import pct_axis
from sov.io import load_questions
from sov.plotting.style import COLORS, FULL, SEQUENTIAL, apply_style, save_fig

NAME = "F06_wartezeit"
SERIES = {
    2019: {"color": "#c3c2b7", "ls": "-"},
    2022: {"color": COLORS["ink2"], "ls": "-"},
    2023: {"color": SEQUENTIAL[3], "ls": "-"},
    2024: {"color": SEQUENTIAL[6], "ls": "-"},
    2025: {"color": SEQUENTIAL[5], "ls": (0, (1, 1.5))},
}
TICKS = {0.1: "6 Min.", 1: "1 Std.", 6: "6 Std.", 24: "1 Tag", 168: "7 Tage"}


def make() -> list[str]:
    apply_style()
    q = load_questions(["year", "is_classic", "first_answer_hours"]).filter(
        pl.col("is_classic") & pl.col("year").is_in(list(SERIES))
    )
    grid = np.logspace(np.log10(0.05), np.log10(config.ANSWER_WINDOW_HOURS), 300)
    fig, ax = plt.subplots(figsize=FULL)
    for h in (1, 24):
        ax.axvline(h, color=COLORS["grid"], lw=0.8, zorder=0)
    for year, st in SERIES.items():
        fa = q.filter(pl.col("year") == year)["first_answer_hours"].fill_null(np.inf).to_numpy()
        fa = np.sort(fa)
        share = np.searchsorted(fa, grid, side="right") / len(fa) * 100
        ax.plot(grid, share, color=st["color"], ls=st["ls"], lw=1.8, label=str(year))
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(FixedLocator(list(TICKS)))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: TICKS.get(round(v, 1), "")))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlim(0.05, config.ANSWER_WINDOW_HOURS)
    ax.set_ylim(0, 80)
    pct_axis(ax)
    ax.set_xlabel("Zeit seit der Frage (Log-Skala)")
    ax.set_ylabel("Fragen mit erster Antwort")
    ax.legend(title="Oktober", loc="upper left", frameon=False, fontsize=7.5, title_fontsize=7.5)
    fig.tight_layout()
    return save_fig(fig, NAME)
