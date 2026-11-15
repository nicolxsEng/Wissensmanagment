"""AP08: Unterbrochene Zeitreihe (plan.md 5.5) an künstlichen Reihen mit bekanntem Ergebnis."""

import math

import numpy as np
import pytest

from sov.its import fit_pretrend, logit, segmented, transform

YEARS = list(range(2015, 2027))
NOISE = [0.01, -0.01, 0.005, -0.005, 0.01, -0.01, 0.0, 0.0, 0.01, -0.01, 0.0, 0.0]


def _series(level_jump: float = math.log(0.5)) -> list[float]:
    """Log-linearer Trend (−5 %/Jahr), ab 2023 Niveausprung um level_jump, kleines Rauschen."""
    out = []
    for i, y in enumerate(YEARS):
        v = 10.0 - 0.05 * (y - 2022) + NOISE[i] + (level_jump if y > 2022 else 0.0)
        out.append(math.exp(v))
    return out


def test_transform_roundtrip():
    assert transform([math.e], "log") == pytest.approx([1.0])
    assert logit(0.5) == 0
    assert transform([0.5], "logit") == pytest.approx([0.0])


def test_pretrend_extrapolation_finds_drop():
    res = fit_pretrend(YEARS, _series(), scale="log")
    post = {r["year"]: r for r in res if r["year"] > 2022}
    # Halbierung -> etwa −50 % gegenüber der Fortschreibung, außerhalb des Intervalls
    for y in (2023, 2024, 2025, 2026):
        assert post[y]["deviation_pct"] == pytest.approx(-50, abs=3)
        assert post[y]["outside_pi"] == "darunter"
    pre = [r for r in res if r["year"] <= 2022]
    assert all(r["outside_pi"] == "" for r in pre)
    assert all(not np.isnan(r["expected"]) for r in res)


def test_no_jump_no_deviation():
    res = fit_pretrend(YEARS, _series(level_jump=0.0), scale="log")
    for r in res:
        assert abs(r["deviation_pct"]) < 3
        assert r["outside_pi"] == ""


def test_segmented_level_change():
    seg = {r["term"]: r for r in segmented(YEARS, _series(), scale="log")}
    assert seg["niveau"]["coef"] == pytest.approx(math.log(0.5), abs=0.03)
    assert seg["niveau"]["effect"] == pytest.approx(0.5, abs=0.02)  # Faktor
    assert seg["steigung"]["coef"] == pytest.approx(0.0, abs=0.02)
    assert seg["trend"]["coef"] == pytest.approx(-0.05, abs=0.01)


def test_logit_scale_for_shares():
    shares = [0.20 + 0.01 * i for i in range(8)] + [0.40, 0.42, 0.44, 0.46]
    res = fit_pretrend(YEARS, shares, scale="logit")
    r2023 = next(r for r in res if r["year"] == 2023)
    assert 0 < r2023["expected"] < 1
    assert r2023["outside_pi"] == "darüber"
