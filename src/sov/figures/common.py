"""Gemeinsame Bausteine für die Abbildungen (Stil: plan.md 3.3, sov.plotting.style)."""

import math

import numpy as np
import polars as pl
from matplotlib.axes import Axes
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter, NullLocator

from sov import config
from sov.plotting.style import COLORS, _de_number

LABELS = {
    "n_questions": "Fragen",
    "answers_per_q_mean": "Antworten je Frage",
    "unanswered_share": "Unbeantwortet",
    "first_answer_median_h": "Std. bis zur ersten Antwort (Median)",
    "answered_24h_share": "Antwort innerhalb von 24 h",
    "accepted_share": "Akzeptierte Antwort",
    "body_len_median": "Textlänge ohne Code (Median, Zeichen)",
}
SHORT = {
    "n_questions": "Fragen",
    "answers_per_q_mean": "Antworten je Frage",
    "unanswered_share": "Unbeantwortet",
    "first_answer_median_h": "Wartezeit (Median)",
    "answered_24h_share": "Antwort in 24 h",
    "accepted_share": "Akzeptiert",
    "body_len_median": "Textlänge",
}


# ----------------------------------------------------------------------------- Daten
def metric_series(metric: str, population: str = "klassisch") -> tuple[list[int], list[float]]:
    m = pl.read_csv(config.PROCESSED_DIR / "metrics_yearly.csv")
    s = m.filter((pl.col("population") == population) & (pl.col("metric") == metric)).sort("year")
    return s["year"].to_list(), s["value"].to_list()


def its_rows(metric: str, population: str = "klassisch") -> pl.DataFrame:
    f = pl.read_csv(config.PROCESSED_DIR / "its_fit.csv")
    return f.filter((pl.col("population") == population) & (pl.col("metric") == metric)).sort(
        "year"
    )


# ----------------------------------------------------------------------------- Zeichnen
def plot_observed(
    ax: Axes,
    years: list[int],
    values: list[float],
    color: str,
    scale: float = 1.0,
    lw: float = 1.8,
    ms: float = 3.5,
    label: str | None = None,
) -> None:
    """Beobachtete Reihe; 2025/2026 gepunktet und hohl (nur Bestätigung)."""
    ys = np.asarray(years)
    vs = np.asarray(values, dtype=float) * scale
    main = ys <= config.MAIN_POST_YEAR
    ax.plot(ys[main], vs[main], color=color, lw=lw, marker="o", ms=ms, zorder=3, label=label)
    tail = ys >= config.MAIN_POST_YEAR
    ax.plot(ys[tail], vs[tail], color=color, lw=lw, ls=(0, (1, 1.5)), zorder=3)
    conf = ys > config.MAIN_POST_YEAR
    ax.plot(
        ys[conf], vs[conf], ls="none", marker="o", ms=ms, mfc="white", mec=color, mew=1.1,
        zorder=4,
    )  # fmt: skip


def plot_trend(ax: Axes, fit: pl.DataFrame, scale: float = 1.0, band: bool = True) -> None:
    """Trend 2015–2022 (durchgezogen) und Fortschreibung mit 95-%-Vorhersageband."""
    pre = fit.filter(pl.col("year") <= config.BASE_YEAR)
    post = fit.filter(pl.col("year") >= config.BASE_YEAR)
    ax.plot(pre["year"], pre["expected"] * scale, color=COLORS["trend"], lw=1.0, zorder=2)
    ax.plot(
        post["year"], post["expected"] * scale, color=COLORS["trend"], lw=1.0,
        ls=(0, (4, 2)), zorder=2,
    )  # fmt: skip
    if band:
        p = fit.filter(pl.col("year") > config.BASE_YEAR)
        ax.fill_between(
            p["year"], p["pi_low"] * scale, p["pi_high"] * scale, color=COLORS["trend_band"],
            lw=0, zorder=1,
        )  # fmt: skip


def pct_axis(ax: Axes, decimals: int = 0) -> None:
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{_de_number(v, decimals)} %"))


def num_axis(ax: Axes, decimals: int = 0) -> None:
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: _de_number(v, decimals)))


def log_axis(ax: Axes, ticks: list[float], decimals: int = 0, axis: str = "y") -> None:
    """Log-Achse mit festen, deutsch formatierten Ticks."""
    a = ax.yaxis if axis == "y" else ax.xaxis
    (ax.set_yscale if axis == "y" else ax.set_xscale)("log")
    a.set_major_locator(FixedLocator(ticks))
    a.set_major_formatter(FuncFormatter(lambda v, _p: _de_number(v, decimals if v < 10 else 0)))
    a.set_minor_locator(NullLocator())
    a.set_minor_formatter(NullFormatter())


def shade_pre_trend(ax: Axes) -> None:
    """Jahre vor dem Trendzeitraum (2008–2014) hell hinterlegen."""
    ax.axvspan(2007.5, config.TREND_START - 0.5, color="#f0efec", lw=0, zorder=0)


def nice_ceil(x: float) -> float:
    e = 10 ** math.floor(math.log10(x))
    for m in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m * e >= x:
            return m * e
    return 10 * e
