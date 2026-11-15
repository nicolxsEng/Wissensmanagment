"""AP06: Stichproben (plan.md AP06) und Speichern von Kodierungen."""

import polars as pl
import pytest

from sov.coding import QUESTION_SHEET_COLUMNS, build_question_sheet, save_entry
from sov.sampling import draw_samples


def _pool():
    rows = []
    qid = 0
    for y in range(2014, 2027):
        for i in range(80):
            qid += 1
            rows.append((qid, y, i % 10 != 0))  # jede 10. Frage ist ein neuer Typ
    return pl.DataFrame(
        rows, schema={"question_id": pl.Int64, "year": pl.Int16, "is_classic": pl.Boolean},
        orient="row",
    )  # fmt: skip


def test_sample_sizes_and_strata():
    s = draw_samples(_pool(), seed=1)
    main = s.filter(pl.col("set") == "stichprobe")
    cal = s.filter(pl.col("set") == "kalibrierung")
    assert main.height == 600 and cal.height == 30
    assert main.group_by("year").len()["len"].to_list() == [50] * 12
    assert set(main["year"]) == set(range(2015, 2027))  # 2014 nicht in der Stichprobe
    dbl = main.filter(pl.col("doppelt")).group_by("year").len()["len"]
    assert dbl.sum() == 150 and set(dbl.to_list()) == {12, 13}
    assert main.filter(pl.col("doppelt"))["split"].unique().to_list() == ["test"]
    assert main.filter(~pl.col("doppelt"))["split"].unique().to_list() == ["train"]


def test_no_overlap_classic_only_reproducible():
    q = _pool()
    s = draw_samples(q, seed=1)
    assert s["question_id"].n_unique() == 630
    classic = set(q.filter(pl.col("is_classic"))["question_id"])
    assert set(s["question_id"]) <= classic
    assert s.equals(draw_samples(q, seed=1))
    assert not s.equals(draw_samples(q, seed=2))


def test_codes_hide_year():
    s = draw_samples(_pool(), seed=1)
    assert s["code"].n_unique() == 630
    ordered = s.sort("code")["year"].to_list()
    assert ordered != sorted(ordered)  # Codes sind nicht nach Jahr geordnet


def test_sheet_and_save_entry(tmp_path):
    sheet = build_question_sheet(["F001", "F002", "F003"], seed=3)
    assert sheet.columns == list(QUESTION_SHEET_COLUMNS)
    p = tmp_path / "b.csv"
    sheet.write_csv(p, separator=";", include_bom=True)
    save_entry(p, "F002", "U", unsicher=True, notiz="Docker")
    df = pl.read_csv(p, separator=";", infer_schema=False)
    row = df.filter(pl.col("code") == "F002").row(0, named=True)
    assert (row["kategorie"], row["unsicher"], row["notiz"]) == ("U", "x", "Docker")
    with pytest.raises(ValueError):
        save_entry(p, "F001", "Q")
