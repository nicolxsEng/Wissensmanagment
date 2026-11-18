"""D29: blinde Prüfung – Stichprobe, Vergleich, Kriterien."""

import pytest

from sov import config
from sov.pruefung import compare, questions_confirmed, stratified_tags, tags_confirmed, wilson


def test_stratified_takes_small_group_whole():
    groups = {"G": [f"g{i:03d}" for i in range(155)], "U": [f"u{i:02d}" for i in range(14)]}
    s = stratified_tags(groups, 40, seed=1)
    assert len(s) == 40 and len(set(s)) == 40
    assert set(groups["U"]) <= set(s)
    assert s == stratified_tags(groups, 40, seed=1)
    big = {"G": [f"g{i}" for i in range(100)], "U": [f"u{i}" for i in range(30)]}
    assert sum(t.startswith("u") for t in stratified_tags(big, 40, seed=1)) == 20


def test_wilson():
    lo, hi = wilson(8, 10)
    assert lo == pytest.approx(0.490, abs=1e-3) and hi == pytest.approx(0.943, abs=1e-3)


def test_compare_and_criteria():
    ref = ["G"] * 10 + ["U"] * 10
    human = ["G"] * 10 + ["U"] * 8 + ["K", "G"]
    r = compare(human, ref, list(config.TAG_CATEGORIES))
    assert r["je_klasse"]["G"]["anteil"] == 1.0 and r["je_klasse"]["U"]["k"] == 8
    assert r["kappa"] >= config.KAPPA_MIN
    assert tags_confirmed(r)  # U genau 80 %
    human2 = ["G"] * 10 + ["U"] * 7 + ["G"] * 3
    assert not tags_confirmed(compare(human2, ref, list(config.TAG_CATEGORIES)))
    assert questions_confirmed(compare(human2, ref, list(config.QUESTION_CATEGORIES)))
