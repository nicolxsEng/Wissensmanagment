"""F01: Fragen je Oktober 2008–2026; rechts Log-Skala mit neuen Fragetypen (TF1, Pflicht)."""

import matplotlib.pyplot as plt

from sov import config
from sov.figures.common import log_axis, metric_series, num_axis, plot_observed
from sov.plotting.style import (
    COLORS,
    FULL,
    _de_number,
    add_chatgpt_marker,
    apply_style,
    save_fig,
    year_axis,
)

NAME = "F01_fragen"


def make() -> list[str]:
    apply_style()
    years, alle = metric_series("n_questions", "alle")
    _, klass = metric_series("n_questions", "klassisch")
    ny, neu = metric_series("n_questions", "neue_typen")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw={"width_ratios": [1.9, 1]})

    # links: lineare Achse, alle Fragen
    plot_observed(a, years, alle, COLORS["gesamt"])
    a.set_ylim(0, 200_000)
    num_axis(a)
    a.set_ylabel("Fragen im Oktober")
    year_axis(a, 2008, 2026, 3)
    add_chatgpt_marker(a)
    offsets = {2015: ((0, 7), "center", "bottom"), 2022: ((-6, -2), "right", "top"),
               2024: ((6, 3), "left", "bottom")}  # fmt: skip
    for y, (xy, ha, va) in offsets.items():
        v = alle[years.index(y)]
        a.annotate(
            _de_number(v, 0), (y, v), xytext=xy, textcoords="offset points", ha=ha, va=va,
            fontsize=7.5, color=COLORS["ink2"],
        )  # fmt: skip

    # rechts: Log-Skala ab 2015, klassische Fragen + neue Fragetypen
    sel = [i for i, y in enumerate(years) if y >= config.TREND_START]
    plot_observed(b, [years[i] for i in sel], [klass[i] for i in sel], COLORS["gesamt"])
    b.plot(ny, neu, ls="none", marker="D", ms=4, color=COLORS["neue_typen"], zorder=5)
    b.annotate(
        "neue\nFragetypen", (ny[0], neu[0]), xytext=(-7, 0), textcoords="offset points",
        ha="right", va="center", fontsize=7.5, color=COLORS["neue_typen"],
    )  # fmt: skip
    log_axis(b, [10, 100, 1_000, 10_000, 100_000])
    b.set_ylim(20, 400_000)
    b.set_ylabel("Fragen (Log-Skala)")
    year_axis(b, config.TREND_START, 2026, 3)
    add_chatgpt_marker(b, label=False)
    fig.tight_layout(w_pad=2)
    return save_fig(fig, NAME)
