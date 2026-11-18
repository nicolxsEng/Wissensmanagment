import numpy as np
import polars as pl
import pytest

from sov import config
from sov.groups import (
    TagMatrix,
    distance,
    group_shares,
    index_distance,
    leave_one_out,
    permutation_summary,
    random_group_shares,
    tag_shift,
)


@pytest.fixture
def q():
    # 2022: 10 Fragen, 4 mit g-Tag, 2 mit u-Tag (eine davon mit beiden)
    # 2024: 10 Fragen, 1 mit g-Tag, 3 mit u-Tag
    rows = (
        [(2022, ["a"]), (2022, ["a", "b"]), (2022, ["b"]), (2022, ["a", "x"]), (2022, ["x", "a"])]
        + [(2022, ["x"])] * 4
        + [(2022, ["x", "y"])]
        + [(2024, ["b"]), (2024, ["x"]), (2024, ["x"]), (2024, ["x"])]
        + [(2024, ["z"])] * 6
    )
    return pl.DataFrame({"year": [r[0] for r in rows], "tags": [r[1] for r in rows]})


def test_group_shares_and_index(q):
    s = group_shares(q, {"G": ["a", "b"], "U": ["x"]})
    g = {r["year"]: r for r in s.filter(pl.col("gruppe") == "G").to_dicts()}
    assert g[2022]["n_group"] == 5 and g[2022]["n_total"] == 10  # Frage mit a und b zählt einmal
    assert g[2024]["share"] == pytest.approx(0.1)
    assert g[2024]["index"] == pytest.approx(0.1 / 0.5 * 100)
    u = {r["year"]: r for r in s.filter(pl.col("gruppe") == "U").to_dicts()}
    assert u[2022]["n_group"] == 7 and u[2024]["n_group"] == 3
    assert distance(s, 2024) == pytest.approx(u[2024]["index"] - g[2024]["index"])


def test_exclusive_drops_overlap(q):
    s = group_shares(q, {"G": ["a", "b"], "U": ["x"]}, exclusive=True)
    g22 = s.filter((pl.col("gruppe") == "G") & (pl.col("year") == 2022))["n_group"].item()
    assert g22 == 3  # zwei Fragen mit a und x fallen weg


def test_tagmatrix_matches_polars(q):
    tags = ["a", "b", "x", "y", "z"]
    tm = TagMatrix(q, tags, [2022, 2024])
    sh = tm.shares(tm.indicator([["a", "b"], ["x"]]))
    ref = group_shares(q, {"G": ["a", "b"], "U": ["x"]})
    for j, gname in enumerate(("G", "U")):
        for i, y in enumerate((2022, 2024)):
            exp = ref.filter((pl.col("gruppe") == gname) & (pl.col("year") == y))["share"].item()
            assert sh[i, j] == pytest.approx(exp)


def test_random_groups_disjoint_and_reproducible(q):
    tm = TagMatrix(q, ["a", "b", "x", "y", "z"], [2022, 2024])
    g1, u1 = random_group_shares(tm, 2, 1, n_perm=50, seed=1)
    g2, u2 = random_group_shares(tm, 2, 1, n_perm=50, seed=1)
    assert np.array_equal(g1, g2) and np.array_equal(u1, u2)
    assert g1.shape == (2, 50)


def test_permutation_summary():
    r = permutation_summary(5.0, np.array([1.0, 2.0, 6.0, np.nan]))
    assert r["n_perm"] == 3 and r["k_ge"] == 1 and r["p"] == pytest.approx(0.5)


def test_leave_one_out_and_index_distance(q):
    tm = TagMatrix(q, ["a", "b", "x", "y", "z"], [2022, 2024])
    loo = leave_one_out(tm, ["a", "b"], ["x", "y"], 2024, 2022)
    assert loo.height == 4
    sh = tm.shares(tm.indicator([["a"], ["x", "y"]]))
    d = index_distance(tm, sh[:, [0]], sh[:, [1]], 2024, 2022)[0]
    ref = group_shares(q, {"G": ["a"], "U": ["x", "y"]})
    exp = distance(ref, 2024)
    assert d == pytest.approx(exp)
    assert loo.filter(pl.col("ohne_tag") == "b")["abstand"].item() == pytest.approx(exp)


def test_tag_shift(q):
    q2 = pl.concat([q, pl.DataFrame({"year": [2019] * 4, "tags": [["a"], ["x"], ["x"], ["z"]]})])
    t = tag_shift(q2, ["a", "x"]).to_dicts()
    a = next(r for r in t if r["tag"] == "a")
    assert a["n_2022"] == 4 and a["n_2024"] == 0 and a["behalten"] == 0
    assert a["vortrend"] == pytest.approx((4 / 10) / (1 / 4))


@pytest.mark.skipif(not config.QUESTIONS_PARQUET.exists(), reason="Daten fehlen")
def test_reproduces_projektstand():
    """Projektstand 8.3: 20+20 Tags, alle Fragen, rohe Tags -> Index 2024 52,5 und 129,1."""
    from sov.io import load_questions

    g = [
        "list",
        "dictionary",
        "pandas",
        "for-loop",
        "arrays",
        "oop",
        "string",
        "function",
        "csv",
        "if-statement",
        "dataframe",
        "loops",
        "regex",
        "recursion",
        "class",
        "json",
        "sql",
        "sorting",
        "numpy",
        "algorithm",
    ]  # noqa: SIM905
    u = [
        "git",
        "github",
        "github-actions",
        "docker",
        "docker-compose",
        "kubernetes",
        "windows",
        "linux",
        "macos",
        "ubuntu",
        "vs-code",
        "visual-studio",
        "xcode",
        "android-studio",
        "azure",
        "amazon-web-services",
        "google-cloud-platform",
        "npm",
        "pip",
        "nginx",
    ]  # noqa: SIM905
    q = load_questions(["year", "tags"], canonical_tags=False)
    s = group_shares(q, {"G": g, "U": u})
    idx = {(r["gruppe"], r["year"]): r["index"] for r in s.to_dicts()}
    assert round(idx[("G", 2024)], 1) == 52.5
    assert round(idx[("U", 2024)], 1) == 129.1
