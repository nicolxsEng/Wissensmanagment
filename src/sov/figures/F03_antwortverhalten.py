"""F03 (Hauptauswertung) und F05 (Gegenprobe Score ≥ 1): Antwortverhalten K2–K6 als
kleine Felder mit Trend 2015–2022 und Fortschreibung (TF1)."""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from sov.figures.common import (
    LABELS,
    its_rows,
    metric_series,
    num_axis,
    pct_axis,
    plot_observed,
    plot_trend,
    shade_pre_trend,
)
from sov.plotting.style import COLORS, FULL_TALL, add_chatgpt_marker, apply_style, save_fig

PANELS = [
    "answers_per_q_mean",
    "unanswered_share",
    "first_answer_median_h",
    "answered_24h_share",
    "accepted_share",
]


def _key(ax, main_label: str, second: str | None = None) -> None:
    ax.axis("off")
    h = [
        Line2D([], [], color=COLORS["gesamt"], marker="o", ms=3.5, lw=1.8, label=main_label),
        Line2D(
            [],
            [],
            color=COLORS["gesamt"],
            marker="o",
            ms=3.5,
            mfc="white",
            ls=(0, (1, 1.5)),
            label="2025/2026 (kleine Fallzahl)",
        ),  # fmt: skip
        Line2D([], [], color=COLORS["trend"], lw=1.0, label="Trend 2015–2022"),
        Line2D([], [], color=COLORS["trend"], lw=1.0, ls=(0, (4, 2)), label="Fortschreibung"),
        Patch(color=COLORS["trend_band"], label="95-%-Vorhersageintervall"),
        Patch(color="#f0efec", label="vor dem Trendzeitraum"),
    ]
    if second:
        h.insert(1, Line2D([], [], color=COLORS["drittes"], lw=1.2, label=second))
    ax.legend(handles=h, loc="center left", frameon=False, fontsize=7.5, handlelength=2.6)


def _make(population: str, name: str, main_label: str, compare: str | None = None) -> list[str]:
    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=FULL_TALL, sharex=True)
    for i, (ax, metric) in enumerate(zip(axes.flat, PANELS, strict=False)):
        share = metric.endswith("_share")
        scale = 100 if share else 1
        shade_pre_trend(ax)
        plot_trend(ax, its_rows(metric, population), scale=scale)
        if compare:
            cy, cv = metric_series(metric, compare)
            ax.plot(cy, [v * scale for v in cv], color=COLORS["drittes"], lw=1.2, zorder=2)
        years, values = metric_series(metric, population)
        plot_observed(ax, years, values, COLORS["gesamt"], scale=scale, ms=2.8, lw=1.5)
        (pct_axis if share else num_axis)(ax, 0 if share else 1)
        ax.set_title(LABELS[metric], loc="left", fontsize=8.5, color=COLORS["gesamt"])
        ax.set_xlim(2007.5, 2026.5)
        ax.set_xticks(range(2008, 2027, 6))
        ax.set_ylim(bottom=0)
        add_chatgpt_marker(ax, label=(i == 0))
    axes[0, 2].tick_params(labelbottom=True)  # unter dieser Spalte steht nur die Legende
    _key(axes.flat[-1], main_label, second=compare and "alle klassischen Fragen")
    fig.tight_layout(h_pad=1.6, w_pad=1.4)
    return save_fig(fig, name)


def make() -> list[str]:
    return _make("klassisch", "F03_antwortverhalten", "beobachtet")


def make_f05() -> list[str]:
    """Gegenprobe: nur Fragen mit Score ≥ 1 (schwarz, eigener Trend), alle klassischen grau."""
    return _make(
        "score_ge_1", "F05_antwortverhalten_score1", "Fragen mit Score ≥ 1", compare="klassisch"
    )
