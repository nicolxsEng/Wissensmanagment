"""F18: KI-Bezug – Anteil der Fragen mit KI-Tag 2015–2026; häufigste KI-Tags 2023–2026 (TF3).

KI-Tags nach Zusammenführen der Synonyme (D15). Anzahl = klassische Fragen, alle Oktober
2023–2026 zusammen.
"""

import matplotlib.pyplot as plt
import polars as pl

from sov import config
from sov.figures.common import metric_series, pct_axis, plot_observed
from sov.plotting.style import (
    COLORS,
    FULL,
    _de_number,
    add_chatgpt_marker,
    apply_style,
    save_fig,
    year_axis,
)

NAME = "F18_ki_bezug"
TOP_N = 10


def make() -> list[str]:
    apply_style()
    years, share = metric_series("ai_share")
    sel = [i for i, y in enumerate(years) if y >= config.TREND_START]
    ai = pl.read_csv(config.PROCESSED_DIR / "ai_tags_yearly.csv")
    top = (
        ai.filter(pl.col("year") > config.BASE_YEAR)
        .group_by("tag")
        .agg(pl.col("n").sum())
        .filter(pl.col("n") > 0)
        .sort("n", descending=True)
        .head(TOP_N)
        .sort("n")
    )
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw={"width_ratios": [1.3, 1]})
    plot_observed(a, [years[i] for i in sel], [share[i] for i in sel], COLORS["gesamt"],
                  scale=100)  # fmt: skip
    pct_axis(a, 1)
    a.set_ylim(0, 2.2)
    a.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
    a.set_ylabel("Fragen mit mindestens einem KI-Tag")
    year_axis(a, config.TREND_START, 2026, 2)
    add_chatgpt_marker(a)

    b.barh(top["tag"], top["n"], color=COLORS["ink2"], height=0.65)
    for tag, n in zip(top["tag"], top["n"], strict=True):
        b.annotate(
            _de_number(n, 0), (n, tag), xytext=(3, 0), textcoords="offset points",
            va="center", fontsize=7.5, color=COLORS["ink2"],
        )  # fmt: skip
    b.set_xlim(0, top["n"].max() * 1.18)
    b.grid(axis="y", visible=False)
    b.grid(axis="x", visible=True)
    b.set_xlabel("Fragen 2023–2026 (Oktober)")
    b.tick_params(axis="y", labelsize=7.5)
    fig.tight_layout(w_pad=2)
    return save_fig(fig, NAME)
