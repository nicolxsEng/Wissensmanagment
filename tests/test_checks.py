"""Tests für die Datenprüfung (AP12): Ziehung, API-Merkmale, Abgleich mit Erklärung."""

from datetime import UTC, datetime

import polars as pl

from sov.checks import api_features, compare_question, draw_check_questions

T0 = int(datetime(2022, 10, 3, 12, tzinfo=UTC).timestamp())
H = 3600


def _questions() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "question_id": [1, 2, 3, 4, 5, 6, 7],
            "year": [2024, 2024, 2025, 2025, 2025, 2026, 2026],
            "is_new_type": [False, False, False, False, True, False, True],
        }
    )


def test_draw_one_per_year_plus_new_type():
    q = _questions()
    s = draw_check_questions(q, seed=1)
    assert s.height == 3 + 1  # drei Jahre + eine Frage eines neuen Typs
    assert sorted(s.filter(~pl.col("extra"))["year"].to_list()) == [2024, 2025, 2026]
    extra = s.filter(pl.col("extra"))
    assert extra["question_id"].item() in (5, 7)
    assert s["question_id"].n_unique() == s.height  # keine Frage doppelt
    assert s.equals(draw_check_questions(q, seed=1))  # wiederholbar


def test_draw_extra_not_already_drawn():
    # 2026 hat nur die neue Frage 7; sie darf nicht doppelt gezogen werden
    q = pl.DataFrame({"question_id": [1, 7], "year": [2025, 2026], "is_new_type": [False, True]})
    s = draw_check_questions(q, seed=3)
    assert s.height == 2
    assert s["question_id"].n_unique() == 2


def _item() -> dict:
    return {"question_id": 10, "creation_date": T0, "tags": ["python", "pandas"],
            "answer_count": 3, "accepted_answer_id": 102}  # fmt: skip


def _answers() -> list[dict]:
    return [
        {"answer_id": 101, "creation_date": T0 + 2 * H, "is_accepted": False},
        {"answer_id": 102, "creation_date": T0 + 30 * H, "is_accepted": True},
        {"answer_id": 103, "creation_date": T0 + 8 * 24 * H, "is_accepted": False},  # außerhalb
    ]


def test_api_features_window():
    f = api_features(_item(), _answers())
    assert f["answer_count_now"] == 3
    assert f["n_answers_7d"] == 2
    assert f["first_answer_hours"] == 2.0
    assert f["accepted_7d"] is True
    assert f["answer_ids_7d"] == {101, 102}
    assert f["tags"] == ["pandas", "python"]
    assert f["created"] == datetime(2022, 10, 3, 12, tzinfo=UTC)


def test_api_features_no_answers():
    f = api_features({**_item(), "answer_count": 0, "accepted_answer_id": None}, [])
    assert f["n_answers_7d"] == 0
    assert f["first_answer_hours"] is None
    assert f["accepted_7d"] is False


def _stored(**kw) -> dict:
    base = {"created": datetime(2022, 10, 3, 12, tzinfo=UTC), "tags": ["pandas", "python"],
            "n_answers_7d": 2, "first_answer_hours": 2.0, "accepted_7d": True,
            "answer_count_now": 3, "answer_ids_7d": {101, 102}}  # fmt: skip
    return {**base, **kw}


def _row(rows, feld):
    return next(r for r in rows if r["feld"] == feld)


def test_compare_identical():
    rows = compare_question(_stored(), api_features(_item(), _answers()))
    assert all(r["gleich"] for r in rows)
    assert all(r["erklaerung"] == "" for r in rows)


def test_compare_deleted_answer_explained():
    # gespeichert war eine dritte Antwort im Fenster, die es heute nicht mehr gibt
    st = _stored(n_answers_7d=3, answer_ids_7d={100, 101, 102}, first_answer_hours=1.0)
    rows = compare_question(st, api_features(_item(), _answers()))
    r = _row(rows, "Antworten im Fenster")
    assert not r["gleich"]
    assert "1 Antwort im Fenster seit dem Abruf gelöscht" in r["erklaerung"]
    assert "gelöscht" in _row(rows, "Zeit bis zur ersten Antwort (h)")["erklaerung"]


def test_compare_question_deleted():
    rows = compare_question(_stored(), None)
    assert all(not r["gleich"] for r in rows)
    assert "gelöscht" in rows[0]["erklaerung"]


def test_compare_tags_and_accept_changed():
    api = api_features({**_item(), "tags": ["python"], "accepted_answer_id": None},
                       [{**a, "is_accepted": False} for a in _answers()])  # fmt: skip
    rows = compare_question(_stored(), api)
    assert "bearbeitet" in _row(rows, "Tags")["erklaerung"]
    assert "Akzeptanz" in _row(rows, "akzeptiert im Fenster")["erklaerung"]


def test_compare_new_type_tag_removed():
    st = _stored(tags=["advice", "pandas", "python"])
    rows = compare_question(st, api_features(_item(), _answers()))
    assert "neuen Fragetyps" in _row(rows, "Tags")["erklaerung"]


def test_draw_answers_reproducible():
    from sov.checks import draw_check_answers

    a = pl.DataFrame({"answer_id": list(range(1, 51)), "in_window": [True] * 40 + [False] * 10})
    s = draw_check_answers(a, 10, seed=5)
    assert len(s) == 10 and len(set(s)) == 10
    assert all(i <= 40 for i in s)  # nur Antworten im Fenster
    assert s == draw_check_answers(a, 10, seed=5)


def test_compare_answer():
    from sov.checks import compare_answer, owner_hash

    st = {"question_id": 10, "created": datetime(2022, 10, 3, 14, tzinfo=UTC),
          "is_accepted": True, "owner": owner_hash(77)}  # fmt: skip
    api = {"answer_id": 1, "question_id": 10, "creation_date": T0 + 2 * H,
           "is_accepted": True, "owner": owner_hash(77)}  # fmt: skip
    r = compare_answer(st, api)
    assert r["gleich"] and r["konto_gleich"] and r["erklaerung"] == ""
    r = compare_answer(st, {**api, "owner": None})
    assert not r["konto_gleich"] and "Konto" in r["erklaerung"]
    r = compare_answer(st, None)
    assert not r["gleich"] and "gelöscht" in r["erklaerung"]
    assert owner_hash(None) is None and owner_hash(77) != "77"
