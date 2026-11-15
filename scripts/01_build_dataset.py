"""AP01: Rohdaten -> data/interim/{questions,answers,texts}.parquet + Datenprotokoll.

uv run python scripts/01_build_dataset.py              # alle Jahre (Zwischenspeicher nutzen)
uv run python scripts/01_build_dataset.py --force      # alles neu
uv run python scripts/01_build_dataset.py --years 2025 2026
"""

import argparse
import time
from datetime import datetime

import polars as pl

from sov import config
from sov.dataset import PARTS_DIR, PROJEKTSTAND_MEDIAN_LEN, build_all


def fmt(n) -> str:
    return f"{n:,}".replace(",", ".")


def write_log(seconds: float) -> str:
    files = sorted(PARTS_DIR.glob("stats_*.parquet"))
    st = pl.concat([pl.read_parquet(f) for f in files]).sort("year")
    rows = st.to_dicts()
    lines = [
        "# Datenprotokoll AP01",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M} · Laufzeit dieses Aufrufs: {seconds:.0f} s · "
        f"Rohdaten: `{config.RAW_DIR}`",
        "",
        "## Umfang und Abgleich mit `_progress.json`",
        "",
        "| Okt. | Fragen | erwartet | Antworten | erwartet | im 7-Tage-Fenster | "
        "ohne Frage | negativer Abstand | ohne Konto | neue Typen | leerer Text | "
        "außerhalb Okt. | Akzeptierte nicht gefunden |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        ok_q = "✓" if r["questions"] == r["questions_expected"] else "✗"
        ok_a = "✓" if r["answers"] == r["answers_expected"] else "✗"
        lines.append(
            f"| {r['year']} | {fmt(r['questions'])} | {fmt(r['questions_expected'])} {ok_q} | "
            f"{fmt(r['answers'])} | {fmt(r['answers_expected'])} {ok_a} | "
            f"{fmt(r['answers_in_window'])} | {fmt(r['orphan_answers'])} | "
            f"{fmt(r['negative_delay'])} | {fmt(r['answers_without_owner'])} | "
            f"{fmt(r['new_type'])} | {fmt(r['empty_bodies'])} | {fmt(r['out_of_month'])} | "
            f"{fmt(r['accepted_not_found'])} |"
        )
    tq, ta = sum(r["questions"] for r in rows), sum(r["answers"] for r in rows)
    lines += [
        f"| **Summe** | **{fmt(tq)}** | 2.013.828 | **{fmt(ta)}** | 3.025.782 | | | | | | | | |",
        "",
        "## Textlänge ohne Codeblöcke (Median, Zeichen) gegen Projektstand",
        "",
        "| Okt. | alle Fragen | Projektstand | Differenz | klassische Fragen |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        ref = PROJEKTSTAND_MEDIAN_LEN.get(r["year"])
        diff = r["median_len_all"] - ref
        mark = "" if abs(diff) <= 5 else " ⚠"
        lines.append(
            f"| {r['year']} | {r['median_len_all']:.0f} | {ref} | {diff:+.0f}{mark} | "
            f"{r['median_len_classic']:.0f} |"
        )
    lines += [
        "",
        "## Hinweise",
        "",
        "- *ohne Frage*: Antworten, deren Frage nicht in der Fragendatei desselben Jahres steht.",
        "- *negativer Abstand*: Antwort älter als die Frage (zusammengelegte Fragen); zählt nie.",
        "- *neue Typen*: Tag `advice`/`best-practices` und gestellt ab 1.10.2025 (D02). "
        "Ältere Fragen mit diesen Tags (13 zwischen 2008 und 2020) bleiben klassisch.",
        "- *Akzeptierte nicht gefunden*: `accepted_answer_id` der Frage ohne passende Antwort mit "
        "`is_accepted` im Datensatz.",
        "- Textlänge: `<pre>`-Blöcke entfernt, Inline-`<code>` bleibt, Leerraum zusammengefasst "
        "(`sov.text.split_body`).",
    ]
    out = config.RESULTS_DIR / "logs" / "build_dataset.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(out)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--years", type=int, nargs="*")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    t0 = time.perf_counter()
    print(f"AP01: baue {'alle Jahre' if not args.years else args.years} …")
    build_all(args.years, workers=args.workers, force=args.force)
    path = write_log(time.perf_counter() - t0)
    print(f"Fertig in {time.perf_counter() - t0:.0f} s. Protokoll: {path}")


if __name__ == "__main__":
    main()
