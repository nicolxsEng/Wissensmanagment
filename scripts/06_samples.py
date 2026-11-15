"""AP06: Stichproben, blinde Ansicht und Kodierbögen für die Fragetexte.

uv run python scripts/06_samples.py

Erzeugt in coding/questions/:
  stichprobe_intern.csv   Code -> Frage, Jahr, Menge, doppelt, Split   (NICHT vor AP09 öffnen)
  split.csv               Code -> train/test (Testmenge = 150 Doppelte, gesperrt für AP10)
  ansicht.parquet         Code, Titel, HTML-Text – ohne Jahr, Tags, Score (für die Kodier-App)
  kalibrierung_A/B.csv    30 Kalibrierungsfragen, je eigene Reihenfolge
  kodierer_A.csv          600 Fragen (Nicolas), kodierer_B.csv 150 Fragen (Gentian)
Bögen mit Einträgen werden nie überschrieben.
"""

from concurrent.futures import ProcessPoolExecutor

import polars as pl

from sov import config
from sov.coding import build_question_sheet, write_sheet
from sov.io import iter_jsonl_gz, load_questions, raw_year_dir
from sov.sampling import draw_samples
from sov.text import clean_title

OUT = config.CODING_DIR / "questions"


def _raw_bodies(args: tuple[int, list[int]]) -> list[dict]:
    year, ids = args
    wanted = set(ids)
    rows = []
    for r in iter_jsonl_gz(raw_year_dir(year) / "questions.jsonl.gz"):
        if r["question_id"] in wanted:
            rows.append(
                {"question_id": r["question_id"], "title": clean_title(r.get("title")),
                 "body_html": r.get("body") or ""}
            )  # fmt: skip
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    q = load_questions(["question_id", "year", "is_classic"], canonical_tags=False)
    s = draw_samples(q)
    s = s.with_columns(link=pl.format("https://stackoverflow.com/q/{}", "question_id"))

    intern = OUT / "stichprobe_intern.csv"
    if intern.exists():
        old = pl.read_csv(intern)
        if old.select("code", "question_id").sort("code").to_dicts() != (
            s.select("code", "question_id").sort("code").to_dicts()
        ):
            raise SystemExit(f"{intern} weicht von der neu gezogenen Stichprobe ab – Abbruch.")
    s.write_csv(intern)
    s.filter(pl.col("set") == "stichprobe").select("code", "split").write_csv(OUT / "split.csv")

    # Blinde Ansicht: Original-HTML aus den Rohdaten, ohne Jahr/Tags/Score
    jobs = [
        (y, s.filter(pl.col("year") == y)["question_id"].to_list())
        for y in sorted(s["year"].unique().to_list())
    ]
    with ProcessPoolExecutor(max_workers=8) as ex:
        rows = [r for part in ex.map(_raw_bodies, jobs) for r in part]
    view = (
        pl.DataFrame(rows)
        .join(s.select("code", "question_id"), on="question_id")
        .select("code", "title", "body_html")
        .sort("code")
    )
    assert view.height == s.height, (view.height, s.height)
    view.write_parquet(OUT / "ansicht.parquet", compression="zstd")

    cal = s.filter(pl.col("set") == "kalibrierung")["code"].to_list()
    main_codes = s.filter(pl.col("set") == "stichprobe")["code"].to_list()
    dbl = s.filter(pl.col("doppelt"))["code"].to_list()
    sheets = {
        "kalibrierung_A.csv": (cal, config.SEED + 11),
        "kalibrierung_B.csv": (cal, config.SEED + 12),
        "kodierer_A.csv": (main_codes, config.SEED + 13),
        "kodierer_B.csv": (dbl, config.SEED + 14),
    }
    for name, (codes, seed) in sheets.items():
        write_sheet(build_question_sheet(codes, seed), OUT / name)
    print(
        f"Fertig: {len(main_codes)} Stichprobe ({len(dbl)} doppelt), {len(cal)} Kalibrierung, "
        f"Ansicht {view.height} Fragen ({(OUT / 'ansicht.parquet').stat().st_size / 1e6:.1f} MB)."
    )


if __name__ == "__main__":
    main()
