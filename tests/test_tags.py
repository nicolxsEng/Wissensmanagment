"""AP03: Kandidaten-Tags und Erkennung von Brüchen in Tag-Zeitreihen."""

import polars as pl

from sov.tags import candidate_tags, detect_breaks, tag_year_counts


def _q(rows):
    return pl.DataFrame(
        rows, schema={"year": pl.Int16, "tags": pl.List(pl.String), "is_classic": pl.Boolean},
        orient="row",
    )  # fmt: skip


def test_candidates_threshold_and_classic_only():
    rows = [(2022, ["a"], True)] * 3 + [(2022, ["b"], True)] * 2 + [(2022, ["b"], False)] * 5
    rows += [(2021, ["c"], True)] * 9
    cands = candidate_tags(_q(rows), year=2022, min_count=3)
    assert cands["tag"].to_list() == ["a"]  # b: nur 2 klassische; c: anderes Jahr


def test_tag_year_counts_has_zeros():
    rows = [(2021, ["a"], True), (2022, ["b"], True)]
    c = tag_year_counts(_q(rows), ["a", "b"], years=[2021, 2022])
    got = {(r["tag"], r["year"]): r["n"] for r in c.to_dicts()}
    assert got[("a", 2022)] == 0 and got[("b", 2021)] == 0
    assert got[("a", 2021)] == 1


def test_detect_breaks():
    # Gesamtzahl Fragen je Jahr fällt um 50 %; Tag "stabil" fällt mit, "abbruch" verschwindet,
    # "klein" verschwindet auch, ist aber zu klein für einen sicheren Befund, "neu" entsteht 2017.
    years = [2015, 2016, 2017, 2018]
    totals = pl.DataFrame({"year": years, "n_year": [10000, 10000, 5000, 5000]})
    data = {
        "stabil": [200, 200, 100, 100],
        "abbruch": [300, 300, 2, 0],
        "klein": [8, 8, 0, 0],
        "neu": [0, 0, 50, 60],
    }
    counts = pl.DataFrame(
        [(t, y, n) for t, ns in data.items() for y, n in zip(years, ns, strict=True)],
        schema={"tag": pl.String, "year": pl.Int64, "n": pl.Int64},
        orient="row",
    )
    br = detect_breaks(counts, totals, min_expected=10, drop_ratio=0.1, birth_min=10)
    kinds = {(r["tag"], r["kind"]): r["year"] for r in br.to_dicts()}
    assert kinds == {("abbruch", "abbruch"): 2017, ("neu", "entsteht"): 2017}


def test_canonicalize_merges_synonyms():
    from sov.tags import canonicalize

    q = _q([(2015, ["old-name", "x"], True), (2024, ["new-name", "old-name"], True)])
    out = canonicalize(q, {"old-name": "new-name"})
    assert out["tags"].to_list() == [["new-name", "x"], ["new-name"]]
