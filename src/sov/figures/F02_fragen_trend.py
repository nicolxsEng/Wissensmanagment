"""F02: Fragen 2015–2026 gegen die Fortschreibung des Trends 2015–2022 (TF1, Pflicht)."""

import matplotlib.pyplot as plt
import polars as pl

from sov import config
from sov.figures.common import its_rows, log_axis, plot_observed, plot_trend
from sov.plotting.style import (
    COLORS,
    FULL,
    _de_number,
    add_chatgpt_marker,
    apply_style,
    save_fig,
    year_axis,
)

NAME = "F02_fragen_trend"


def make() -> list[str]:
    apply_style()
    fit = its_rows("n_questions")
    fig, ax = plt.subplots(figsize=FULL)
    plot_trend(ax, fit)
    plot_observed(ax, fit["year"].to_list(), fit["observed"].to_list(), COLORS["gesamt"])
    log_axis(ax, [1_000, 3_000, 10_000, 30_000, 100_000, 300_000])
    ax.set_ylim(600, 350_000)
    ax.set_ylabel("Fragen im Oktober (Log-Skala)")
    year_axis(ax, config.TREND_START, 2026, 1)
    add_chatgpt_marker(ax, where="bottom")

    last = fit.filter(pl.col("year") == 2026).row(0, named=True)
    ax.annotate(
        "Fortschreibung des Trends\n2015–2022 (95-%-Intervall)", (2026, last["expected"]),
        xytext=(-4, 10), textcoords="offset points", ha="right", va="bottom",
        fontsize=7.5, color=COLORS["ink2"],
    )  # fmt: skip
    for y in (2023, config.MAIN_POST_YEAR):
        r = fit.filter(pl.col("year") == y).row(0, named=True)
        text = f"{_de_number(r['deviation_pct'], 0)} %"
        right = y == 2023  # links davon liegt die ChatGPT-Linie
        ax.annotate(
            text, (y, r["observed"]), xytext=(8, 2) if right else (-6, -5),
            textcoords="offset points", ha="left" if right else "right",
            va="bottom" if right else "top", fontsize=7.5, color=COLORS["gesamt"],
        )  # fmt: skip
    fig.tight_layout()
    return save_fig(fig, NAME)
