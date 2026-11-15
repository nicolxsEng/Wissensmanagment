"""AP04: Kodierbögen für Tags – blind, gleich, unterschiedlich gemischt, nie überschreiben."""

import polars as pl
import pytest

from sov.coding import SHEET_COLUMNS, build_tag_sheet, read_sheet, sheet_has_entries, write_sheet


def _wiki(n=30):
    return pl.DataFrame({"tag": [f"t{i:02d}" for i in range(n)], "wiki_auszug": ["x"] * n})


def test_sheets_same_tags_different_order():
    a = build_tag_sheet(_wiki(), seed=1)
    b = build_tag_sheet(_wiki(), seed=2)
    assert a.columns == list(SHEET_COLUMNS)
    assert sorted(a["tag"]) == sorted(b["tag"])
    assert a["tag"].to_list() != b["tag"].to_list()
    assert a["nr"].to_list() == list(range(1, 31))
    assert build_tag_sheet(_wiki(), seed=1)["tag"].to_list() == a["tag"].to_list()


def test_no_number_columns_and_empty_entries():
    a = build_tag_sheet(_wiki(), seed=1)
    numeric = [c for c, t in a.schema.items() if t.is_numeric()]
    assert numeric == ["nr"]
    assert a["kategorie"].fill_null("").str.len_chars().sum() == 0


def test_never_overwrite_filled_sheet(tmp_path):
    p = tmp_path / "bogen.csv"
    sheet = build_tag_sheet(_wiki(3), seed=1)
    write_sheet(sheet, p)
    assert not sheet_has_entries(p)
    filled = read_sheet(p).with_columns(kategorie=pl.lit("G"))
    filled.write_csv(p, separator=";", include_bom=True)
    assert sheet_has_entries(p)
    with pytest.raises(FileExistsError):
        write_sheet(sheet, p)
