"""AP11: Titelauswahl, NMF und Prüfbögen (BERTopic selbst wird im Skript getestet)."""

import numpy as np
import polars as pl

from sov.topics.core import (
    TOKEN_PATTERN,
    balanced_titles,
    evaluate_checks,
    run_nmf,
    topic_diversity,
    typical_and_check_titles,
)


def test_balanced_titles():
    rows = [(i, 2015 + i % 3, True, f"t{i}") for i in range(300)] + [(999, 2015, False, "x")]
    q = pl.DataFrame(rows, schema=["question_id", "year", "is_classic", "title"], orient="row")
    out = balanced_titles(q, years=[2015, 2016, 2017], per_year=40, seed=1)
    assert out.group_by("year").len()["len"].to_list() == [40, 40, 40]
    assert 999 not in out["question_id"].to_list()
    assert out.equals(balanced_titles(q, years=[2015, 2016, 2017], per_year=40, seed=1))


def test_token_pattern_keeps_programming_tokens():
    import re

    toks = re.findall(TOKEN_PATTERN, "How to use c++ and c# with node.js in python3?")
    assert {"c++", "c#", "node.js", "python3"} <= set(toks)


def test_nmf_separates_obvious_topics():
    titles = [f"docker container port {i}" for i in range(20)] + [
        f"pandas dataframe groupby column {i}" for i in range(20)
    ]
    labels, keywords = run_nmf(titles, k=2, seed=0)
    assert len(set(labels[:20])) == 1 and len(set(labels[20:])) == 1
    assert labels[0] != labels[20]
    assert any("docker" in kw for kw in keywords)


def test_typical_and_check_titles_disjoint():
    labels = np.array([0] * 20 + [1] * 8)
    score = np.linspace(0, 1, 28)
    titles = [f"t{i}" for i in range(28)]
    out = typical_and_check_titles(titles, labels, score, n_typical=5, n_check=10, seed=1)
    t0 = out[0]
    assert len(t0["typical"]) == 5 and len(t0["check"]) == 10
    assert not set(t0["typical"]) & set(t0["check"])
    assert len(out[1]["check"]) == 3  # nur 8 Mitglieder: 5 typisch + 3 zum Prüfen


def test_diversity_and_evaluation():
    assert topic_diversity([["a", "b"], ["a", "c"]]) == 0.75
    checks = pl.DataFrame(
        {
            "code": ["T01"] * 10 + ["T02"] * 10,
            "passt_A": ["j"] * 9 + ["n"] + ["j"] * 7 + ["n"] * 3,
            "passt_B": ["j"] * 8 + ["n"] * 2 + ["j"] * 10,
        }
    )
    ev = {r["code"]: r for r in evaluate_checks(checks).to_dicts()}
    assert ev["T01"]["bestanden"] is True  # 9 und 8 von 10
    assert ev["T02"]["bestanden"] is False  # A nur 7 von 10
