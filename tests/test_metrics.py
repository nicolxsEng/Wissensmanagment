"""AP02: Kennzahlen K1–K9 an einer Mini-Tabelle, deren Werte von Hand ausgerechnet sind."""

import math

import polars as pl
import pytest

from sov.metrics import changes, cohens_h, metrics_long, yearly_metrics


def mini() -> pl.DataFrame:
    # Fragen 1–5 klassisch, Frage 6 neuer Typ
    return pl.DataFrame(
        {
            "year": [2022] * 6,
            "n_answers_7d": [2, 1, 0, 0, 3, 1],
            "answered_7d": [True, True, False, False, True, True],
            "first_answer_hours": [1.0, 30.0, 200.0, None, 5.0, 2.0],
            "answered_24h": [True, False, False, False, True, True],
            "accepted_7d": [True, False, False, False, False, True],
            "body_len_nocode": [100, 200, 300, 400, 500, 600],
            "n_ai_tags": [0, 1, 0, 0, 0, 0],
            "has_code": [True, False, True, False, True, False],
            "is_closed": [False, False, True, False, False, False],
            "score": [3, 0, -1, 1, 2, 0],
            "is_classic": [True, True, True, True, True, False],
            "is_new_type": [False, False, False, False, False, True],
        },
        schema_overrides={"year": pl.Int16, "n_answers_7d": pl.Int16},
    )


def test_classic_metrics_by_hand():
    m = yearly_metrics(mini().filter(pl.col("is_classic"))).row(0, named=True)
    assert m["n_questions"] == 5
    assert m["answers_per_q_mean"] == pytest.approx(1.2)
    assert m["answers_per_q_median"] == 1
    assert m["unanswered_share"] == pytest.approx(0.4)
    # K4: Median nur über Fragen mit Antwort im Fenster (1, 30, 5) -> 5; Frage 3 (200 h) zählt nicht
    assert m["first_answer_median_h"] == pytest.approx(5.0)
    assert m["answered_24h_share"] == pytest.approx(0.4)
    assert m["accepted_share"] == pytest.approx(0.2)
    assert m["body_len_median"] == 300
    assert m["body_len_q25"] == 200
    assert m["body_len_q75"] == 400
    assert m["ai_share"] == pytest.approx(0.2)
    assert m["code_share"] == pytest.approx(0.6)
    assert m["closed_share"] == pytest.approx(0.2)


def test_populations():
    long = metrics_long(mini())
    get = {(r["population"], r["metric"]): r["value"] for r in long.to_dicts()}
    assert get[("alle", "n_questions")] == 6
    assert get[("neue_typen", "n_questions")] == 1
    assert get[("klassisch", "n_questions")] == 5
    # Score >= 1 unter den klassischen: Fragen 1, 4, 5
    assert get[("score_ge_1", "n_questions")] == 3
    assert get[("score_ge_1", "answers_per_q_mean")] == pytest.approx(5 / 3)
    assert get[("score_ge_1", "first_answer_median_h")] == pytest.approx(3.0)
    # Antwortkennzahlen gibt es für "alle" nicht (neue Typen werden ausgeschlossen, D03)
    assert ("alle", "unanswered_share") not in get


def test_cohens_h():
    assert cohens_h(0.5, 0.5) == 0
    expected = 2 * math.asin(math.sqrt(0.4)) - 2 * math.asin(math.sqrt(0.2))
    assert cohens_h(0.2, 0.4) == pytest.approx(expected)


def test_changes():
    long = pl.DataFrame(
        {
            "year": [2022, 2024, 2022, 2024],
            "population": ["klassisch"] * 4,
            "metric": ["n_questions", "n_questions", "unanswered_share", "unanswered_share"],
            "value": [100.0, 25.0, 0.2, 0.4],
        }
    )
    ch = changes(long, base_year=2022, compare_years=[2024])
    rows = {r["metric"]: r for r in ch.to_dicts()}
    assert rows["n_questions"]["pct_change"] == pytest.approx(-75.0)
    assert rows["n_questions"]["cohens_h"] is None
    assert rows["unanswered_share"]["pct_change"] == pytest.approx(100.0)
    assert rows["unanswered_share"]["cohens_h"] == pytest.approx(cohens_h(0.2, 0.4))
