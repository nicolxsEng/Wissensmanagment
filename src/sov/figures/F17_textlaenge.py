"""F17: Textlänge ohne Code (Median mit Interquartilsband) 2008–2026 (TF3, Pflicht).

Das zweite Feld (Textlänge je Gruppe Grundlagen/Umgebung) kommt nach AP05/AP07 hinzu.
"""

import matplotlib.pyplot as plt

from sov.figures.common import (
    its_rows,
    metric_series,
    num_axis,
    plot_observed,
    plot_trend,
)
from sov.plotting.style import COLORS, FULL, add_chatgpt_marker, apply_style, save_fig, year_axis

NAME = "F17_textlaenge"


def make() -> list[str]:
    apply_style()
    years, med = metric_series("body_len_median")
    _, q25 = metric_series("body_len_q25")
    _, q75 = metric_series("body_len_q75")
    fig, ax = plt.subplots(figsize=FULL)
    ax.fill_between(years, q25, q75, color="#e8e7e1", lw=0, zorder=1)
    plot_trend(ax, its_rows("body_len_median"), band=False)
    plot_observed(ax, years, med, COLORS["gesamt"])
    ax.annotate(
        "mittlere 50 % der Fragen", (2012, q75[years.index(2012)]), xytext=(0, 4),
        textcoords="offset points", ha="center", va="bottom", fontsize=7.5,
        color=COLORS["ink2"],
    )  # fmt: skip
    ax.annotate(
        "Median", (2017, med[years.index(2017)]), xytext=(0, 5), textcoords="offset points",
        ha="center", va="bottom", fontsize=7.5, color=COLORS["gesamt"],
    )  # fmt: skip
    ax.annotate(
        "Trend 2015–2022", (2026, its_rows("body_len_median")["expected"][-1]),
        xytext=(-2, -6), textcoords="offset points", ha="right", va="top", fontsize=7.5,
        color=COLORS["ink2"],
    )  # fmt: skip
    ax.set_ylim(0, 1600)
    num_axis(ax)
    ax.set_ylabel("Zeichen im Fragetext ohne Code")
    year_axis(ax, 2008, 2026, 2)
    add_chatgpt_marker(ax)
    fig.tight_layout()
    return save_fig(fig, NAME)
