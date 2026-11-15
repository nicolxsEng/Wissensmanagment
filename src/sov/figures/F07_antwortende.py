"""F07: Sichtbare Antwortende 2008–2026 (AP14; TF1, Pflicht).

Vier Felder: Zahl der Antwortenden (A1, Log-Skala), Antwortende je 100 Fragen, Anteil der
Antworten der aktivsten 10 % (A4), Anteil schon im Vorjahr aktiver Antwortender (A5);
jeweils mit Trend 2015–2022 und Fortschreibung.
"""

import matplotlib.pyplot as plt
import polars as pl

from sov import config
from sov.figures.common import (
    log_axis,
    num_axis,
    pct_axis,
    plot_observed,
    plot_trend,
    shade_pre_trend,
)
from sov.plotting.style import COLORS, FULL_TALL, add_chatgpt_marker, apply_style, save_fig

NAME = "F07_antwortende"
PANELS = [
    ("answerers", "Sichtbare Antwortende (Log-Skala)"),
    ("answerers_per_100q", "Antwortende je 100 Fragen"),
    ("top_share_answers", "Antworten der aktivsten 10 %"),
    ("continuity", "Schon im Vorjahres-Oktober aktiv"),
]


def make() -> list[str]:
    apply_style()
    m = pl.read_csv(config.PROCESSED_DIR / "answerers_yearly.csv")
    fit = pl.read_csv(config.PROCESSED_DIR / "its_answerers.csv")
    fig, axes = plt.subplots(2, 2, figsize=FULL_TALL, sharex=True)
    for i, (ax, (metric, title)) in enumerate(zip(axes.flat, PANELS, strict=True)):
        share = metric in ("top_share_answers", "continuity")
        scale = 100 if share else 1
        s = m.filter(pl.col("metric") == metric).sort("year")
        shade_pre_trend(ax)
        plot_trend(ax, fit.filter(pl.col("metric") == metric).sort("year"), scale=scale)
        plot_observed(ax, s["year"].to_list(), s["value"].to_list(), COLORS["gesamt"],
                      scale=scale, ms=2.8, lw=1.5)  # fmt: skip
        if metric == "answerers":
            log_axis(ax, [300, 1_000, 3_000, 10_000, 30_000, 100_000])
            ax.set_ylim(250, 100_000)
        elif share:
            pct_axis(ax)
            ax.set_ylim(0, 70)
        else:
            num_axis(ax)
            ax.set_ylim(0, 60)
        ax.set_title(title, loc="left", fontsize=8.5, color=COLORS["gesamt"])
        ax.set_xlim(2007.5, 2026.5)
        ax.set_xticks(range(2008, 2027, 3))
        add_chatgpt_marker(ax, label=(i == 0), where="bottom")
    fig.tight_layout(h_pad=1.6, w_pad=2)
    return save_fig(fig, NAME)
