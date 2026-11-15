"""AP10: Eingabetexte, Bewertung, Testsperre und Basisverfahren (ohne große Modelle)."""

import pytest

from sov.classify.candidates import TfidfLogReg
from sov.classify.data import model_input
from sov.classify.evaluate import HoldoutLock, macro_f1_ci


def test_model_input_title_text_code_capped():
    s = model_input("Docker port", "Text [CODE] more", "x = 1\n" * 500, max_chars=300)
    assert s.startswith("Docker port\n\nText [CODE] more")
    assert "Code (Auszug):" in s
    assert len(s) <= 300


def test_model_input_without_code():
    assert model_input("T", "B", "") == "T\n\nB"


def test_macro_f1_ci():
    y = ["G", "U", "S"] * 20
    res = macro_f1_ci(y, y, n_boot=200, seed=1)
    assert res["macro_f1"] == 1.0 and res["ci_low"] == 1.0
    worse = ["G"] * 60
    assert macro_f1_ci(y, worse, n_boot=200, seed=1)["macro_f1"] < 0.5


def test_test_set_lock(tmp_path):
    lock = HoldoutLock(tmp_path / "testlaeufe.json")
    lock.claim("tfidf", note="erste Auswertung")
    with pytest.raises(PermissionError):
        lock.claim("tfidf")
    lock.claim("setfit")  # anderer Kandidat ist erlaubt


def test_tfidf_baseline_learns_toy_data():
    texts = [f"docker compose port {i}" for i in range(15)] + [
        f"list comprehension loop {i}" for i in range(15)
    ]
    labels = ["U"] * 15 + ["G"] * 15
    m = TfidfLogReg().fit(texts, labels)
    assert m.predict(["docker port mapping", "loop over list"]) == ["U", "G"]
