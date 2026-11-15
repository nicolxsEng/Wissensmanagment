"""Einheitlicher Stil für alle Abbildungen (plan.md Abschnitt 3.3).

Verwendung:
    from sov.plotting.style import apply_style, save_fig, COLORS, FULL, add_chatgpt_marker
    apply_style()
    fig, ax = plt.subplots(figsize=FULL)
    ...
    save_fig(fig, "F08_index_gruppen")
"""

from collections.abc import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from sov import config

# Farben nach Bedeutung. Grundlagen/Umgebung/Sonstige = die ersten drei Slots der
# validierten Referenzpalette (auch bei Farbsehschwäche paarweise unterscheidbar).
COLORS = {
    "grundlagen": "#2a78d6",  # Blau
    "umgebung": "#eb6834",  # Orange
    "drittes": "#1baf7a",  # Aqua, nur wenn eine dritte Gruppe Farbe braucht
    "sonstige": "#898781",  # Grau (keine Gruppe / Sonstige)
    "gesamt": "#0b0b0b",  # Schwarz (alle Fragen)
    "trend": "#898781",  # Fortschreibung des Trends (gestrichelt)
    "trend_band": "#e1e0d9",  # Vorhersageintervall
    "ink2": "#52514e",  # Beschriftungen zweiter Ordnung
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
    "neue_typen": "#6250d6",  # Violett: neue Fragetypen ab 2025
}
# Sequenziell (Heatmaps): eine Farbe hell -> dunkel
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
# Divergierend (Gewinner/Verlierer): Blau <-> Grau <-> Rot
DIVERGING = {"neg": "#e34948", "mid": "#f0efec", "pos": "#2a78d6"}

CM = 1 / 2.54
FULL = (16 * CM, 7.5 * CM)  # ganze Textbreite
FULL_TALL = (16 * CM, 11 * CM)
HALF = (7.8 * CM, 6 * CM)  # halbe Textbreite


def apply_style() -> None:
    """Setzt die rcParams für druckfähige Abbildungen."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "axes.titlesize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "legend.frameon": False,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": COLORS["axis"],
            "axes.labelcolor": COLORS["ink2"],
            "xtick.color": COLORS["ink2"],
            "ytick.color": COLORS["ink2"],
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": COLORS["grid"],
            "grid.linewidth": 0.6,
            "lines.linewidth": 1.8,
            "lines.markersize": 4,
            "axes.prop_cycle": mpl.cycler(
                color=[COLORS["grundlagen"], COLORS["umgebung"], COLORS["drittes"]]
            ),
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
            "pdf.fonttype": 42,  # Text bleibt im PDF als Text erhalten
        }
    )


def _de_number(x: float, decimals: int) -> str:
    s = f"{x:,.{decimals}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def de_formatter(decimals: int = 0, suffix: str = "") -> FuncFormatter:
    """Achsenformat mit Tausenderpunkt und Dezimalkomma, z. B. de_formatter(1, ' %')."""
    return FuncFormatter(lambda x, _pos: _de_number(x, decimals) + suffix)


def add_chatgpt_marker(ax: Axes, label: bool = True, where: str = "top") -> None:
    """Senkrechte Linie zwischen Oktober 2022 und Oktober 2023 (ChatGPT am 30.11.2022).

    Die Beschriftung steht links neben der Linie, oben (where="top") oder unten
    ("bottom") – je nachdem, wo im Diagramm Platz ist.
    """
    x = config.BASE_YEAR + 0.5
    ax.axvline(x, color=COLORS["ink2"], lw=0.8, ls=(0, (3, 3)), zorder=0)
    if label:
        top = where == "top"
        ax.annotate(
            "ChatGPT",
            xy=(x, 1 if top else 0),
            xycoords=("data", "axes fraction"),
            xytext=(-3, -2 if top else 2),
            textcoords="offset points",
            ha="right",
            va="top" if top else "bottom",
            fontsize=7.5,
            color=COLORS["ink2"],
        )


def mark_confirmation_years(ax: Axes, years: Iterable[int], values: Iterable[float], color: str):
    """Zeichnet 2025/2026 als hohle Marker (nur Bestätigung, kleine Fallzahlen)."""
    pts = [(y, v) for y, v in zip(years, values, strict=True) if y in config.CONFIRM_YEARS]
    if pts:
        xs, ys = zip(*pts, strict=True)
        ax.plot(xs, ys, ls="none", marker="o", mfc="white", mec=color, mew=1.2, zorder=3)


def label_line_end(ax: Axes, x: float, y: float, text: str, color: str, dy: float = 0) -> None:
    """Direkte Beschriftung am Linienende statt Legende."""
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(4, dy),
        textcoords="offset points",
        va="center",
        fontsize=8,
        color=color,
    )


def year_axis(ax: Axes, start: int = 2008, end: int = 2026, step: int = 2) -> None:
    ax.set_xlim(start - 0.5, end + 0.5)
    ax.set_xticks(range(start, end + 1, step))


def save_fig(fig: Figure, name: str) -> list[str]:
    """Speichert als PDF und PNG in figures/ und schließt die Abbildung."""
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("pdf", "png"):
        p = config.FIGURES_DIR / f"{name}.{ext}"
        fig.savefig(p)
        paths.append(str(p))
    plt.close(fig)
    return paths
