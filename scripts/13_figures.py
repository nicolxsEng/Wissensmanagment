"""AP13: alle Abbildungen erzeugen (figures/*.pdf + *.png).

uv run python scripts/13_figures.py            # alle verfügbaren
uv run python scripts/13_figures.py F01 F04    # nur diese

Abbildungen, deren Eingaben noch fehlen (z. B. Gruppen vor AP05), werden übersprungen.
"""

import sys
from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

from sov.figures import (  # noqa: E402
    F01_fragen,
    F02_fragen_trend,
    F03_antwortverhalten,
    F04_abweichung,
    F06_wartezeit,
    F07_antwortende,
    F17_textlaenge,
    F18_ki_bezug,
    gruppen,
    klassifikation,
)

FIGURES: dict[str, Callable[[], list[str]]] = {
    "F01": F01_fragen.make,
    "F02": F02_fragen_trend.make,
    "F03": F03_antwortverhalten.make,
    "F04": F04_abweichung.make,
    "F05": F03_antwortverhalten.make_f05,
    "F06": F06_wartezeit.make,
    "F07": F07_antwortende.make,
    "F08": gruppen.make_f08,
    "F09": gruppen.make_f09,
    "F10": gruppen.make_f10,
    "F11": gruppen.make_f11,
    "F12": gruppen.make_f12,
    "F13": gruppen.make_f13,
    "F14": klassifikation.make_f14,
    "F15": klassifikation.make_f15,
    "F23": gruppen.make_f23,
    "F17": F17_textlaenge.make,
    "F18": F18_ki_bezug.make,
    # F21 (Top-Tags) erst nach der Tag-Kodierung (AP05), wegen der blinden Einordnung
}


def main() -> None:
    wanted = [a.upper() for a in sys.argv[1:]] or list(FIGURES)
    for fid in wanted:
        if fid not in FIGURES:
            print(f"{fid}: noch nicht umgesetzt oder wartet auf Eingaben – übersprungen")
            continue
        try:
            paths = FIGURES[fid]()
            print(f"{fid}: {paths[0]}")
        except FileNotFoundError as e:
            print(f"{fid}: Eingabe fehlt ({e}) – übersprungen")


if __name__ == "__main__":
    main()
