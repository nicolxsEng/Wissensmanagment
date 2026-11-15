"""AP01: Antwortfenster 0–7 Tage (plan.md 5.2) und abgeleitete Felder je Frage."""

import polars as pl

from sov.dataset import add_answer_features

H = 3600
T0 = 1_665_000_000  # beliebiger Zeitpunkt im Oktober 2022


def _frames():
    q = pl.DataFrame(
        {
            "question_id": [1, 2, 3, 4],
            "created_ts": [T0, T0, T0, T0],
        }
    )
    a = pl.DataFrame(
        {
            "answer_id": [10, 11, 12, 20, 30, 31, 99],
            "question_id": [1, 1, 1, 2, 3, 3, 777],  # 777: Frage fehlt
            "created_ts": [
                T0 + 2 * H,  # Q1 im Fenster, erste Antwort
                T0 + 168 * H,  # Q1 genau an der Grenze -> zählt
                T0 + 168 * H + 1,  # Q1 knapp außerhalb
                T0 + 30 * H,  # Q2 im Fenster, nach 24 h
                T0 - 5 * H,  # Q3 negativer Abstand -> zählt nie
                T0 + 200 * H,  # Q3 außerhalb des Fensters
                T0,
            ],
            "is_accepted": [False, True, False, False, True, True, False],
        }
    )
    return q, a


def test_window_counts_and_first_answer():
    q, a = _frames()
    qf, af, stats = add_answer_features(q, a)
    qf = qf.sort("question_id")
    assert qf["n_answers_7d"].to_list() == [2, 1, 0, 0]
    assert qf["answered_7d"].to_list() == [True, True, False, False]
    assert qf["first_answer_hours"].to_list() == [2.0, 30.0, 200.0, None]
    assert qf["answered_24h"].to_list() == [True, False, False, False]
    # Q1: akzeptierte Antwort liegt im Fenster (Grenze); Q3: nur außerhalb bzw. negativ
    assert qf["accepted_7d"].to_list() == [True, False, False, False]
    assert stats == {"orphan_answers": 1, "negative_delay": 1}


def test_answer_rows_flags():
    q, a = _frames()
    _, af, _ = add_answer_features(q, a)
    af = af.sort("answer_id")
    assert af["in_window"].to_list() == [True, True, False, True, False, False, False]
    assert af.filter(pl.col("answer_id") == 30)["delay_hours"].item() == -5.0
    assert af.filter(pl.col("answer_id") == 99)["delay_hours"].item() is None


def test_new_type_needs_tag_and_date():
    """Alte Fragen mit Tag best-practices bleiben klassisch (D02)."""
    from sov import config

    new_from = int(config.NEW_TYPE_START.timestamp())
    q = pl.DataFrame(
        {
            "tags": [["best-practices"], ["advice", "java"], ["java"]],
            "created_ts": [new_from - 1, new_from, new_from],
        }
    )
    tags = sorted(config.NEW_TYPE_TAGS)
    out = q.select(
        pl.col("tags").list.eval(pl.element().is_in(tags)).list.any()
        & (pl.col("created_ts") >= new_from)
    ).to_series()
    assert out.to_list() == [False, True, False]
