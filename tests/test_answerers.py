"""AP14: Sichtbare Antwortende (A1, A3 gesamt, A4, A5) an Mini-Daten mit Handrechnung."""

import polars as pl
import pytest

from sov.answerers import OUTPUT_COLUMNS, answerer_metrics


def _data():
    q = pl.DataFrame(
        {
            "question_id": [1, 2, 3, 4, 5],
            "year": [2021, 2021, 2022, 2022, 2022],
            "is_classic": [True, True, True, True, False],
        },
        schema_overrides={"year": pl.Int16},
    )
    a = pl.DataFrame(
        {
            "question_id": [1, 1, 2, 2, 2, 3, 3, 4, 4, 3, 5],
            "owner_user_id": [1, 1, 1, 2, 3, 1, 4, 4, None, 7, 9],
            "in_window": [True] * 9 + [False, True],
        },
        schema_overrides={"owner_user_id": pl.Int64},
    )
    return q, a


def _get(df, year, metric):
    return df.filter((pl.col("year") == year) & (pl.col("metric") == metric))["value"].item()


def test_by_hand():
    q, a = _data()
    m = answerer_metrics(q, a, expert_min=3, top_share=0.10)
    # 2021: Nutzer 1 (3 Antworten), 2 (1), 3 (1)
    assert _get(m, 2021, "answerers") == 3
    assert _get(m, 2021, "experts") == 1
    assert _get(m, 2021, "top_share_answers") == pytest.approx(3 / 5)  # ceil(0,3) = 1 Person
    assert _get(m, 2021, "answerers_per_100q") == pytest.approx(3 / 2 * 100)
    # 2022: Nutzer 1 (1), 4 (2), ohne Konto (1); Nutzer 7 außerhalb des Fensters,
    # Nutzer 9 antwortet auf neuen Fragetyp -> beide zählen nicht
    assert _get(m, 2022, "answerers") == 2
    assert _get(m, 2022, "answers_without_owner_share") == pytest.approx(1 / 4)
    assert _get(m, 2022, "top_share_answers") == pytest.approx(2 / 3)
    assert _get(m, 2022, "continuity") == pytest.approx(1 / 2)  # Nutzer 1 war 2021 dabei


def test_no_user_ids_in_output():
    q, a = _data()
    m = answerer_metrics(q, a)
    assert m.columns == list(OUTPUT_COLUMNS)
    assert not any("user" in c for c in m.columns)
