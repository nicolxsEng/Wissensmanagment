"""Datenprüfung (AP12): Stichprobe von Fragen erneut über die API abfragen und vergleichen.

Verglichen werden die Felder, aus denen die Kennzahlen entstehen (Erstellzeit, Tags, Antworten im
7-Tage-Fenster, Zeit bis zur ersten Antwort, akzeptierte Antwort im Fenster) und zusätzlich der
heutige `answer_count`. Abweichungen werden, soweit möglich, aus den Daten erklärt (z. B. seit dem
Abruf gelöschte Antworten). Nutzer-IDs werden weder gespeichert noch ausgegeben.
"""

import hashlib
import json
import time
from datetime import UTC, datetime

import numpy as np
import polars as pl

from sov import config

WINDOW_H = config.ANSWER_WINDOW_HOURS
CACHE = config.INTERIM_DIR / "api_cache" / "datenpruefung.json"
CACHE_A = config.INTERIM_DIR / "api_cache" / "datenpruefung_antworten.json"
FIELDS = (
    "Erstellzeit",
    "Tags",
    "Antworten im Fenster",
    "Zeit bis zur ersten Antwort (h)",
    "akzeptiert im Fenster",
    "Antworten heute (answer_count)",
)


def draw_check_questions(q: pl.DataFrame, seed: int) -> pl.DataFrame:
    """Je Jahr eine zufällige Frage (alle Fragen des Oktobers), dazu eine Frage eines neuen
    Fragetyps, die noch nicht gezogen ist. Erwartet question_id, year, is_new_type."""
    rng = np.random.default_rng(seed)
    rows = []
    for y in sorted(q["year"].unique().to_list()):
        ids = sorted(q.filter(pl.col("year") == y)["question_id"].to_list())
        rows.append({"question_id": int(rng.choice(ids)), "year": y, "extra": False})
    drawn = {r["question_id"] for r in rows}
    pool = sorted(set(q.filter(pl.col("is_new_type"))["question_id"].to_list()) - drawn)
    if pool:
        qid = int(rng.choice(pool))
        year = q.filter(pl.col("question_id") == qid)["year"].item()
        rows.append({"question_id": qid, "year": year, "extra": True})
    return pl.DataFrame(rows).sort("extra", "year")


def api_features(item: dict, answers: list[dict]) -> dict:
    """Merkmale einer Frage aus der heutigen API-Antwort (Definition wie in AP01, plan.md 5.2)."""
    t0 = item["creation_date"]
    delays = {a["answer_id"]: (a["creation_date"] - t0) / 3600 for a in answers}
    in_win = {i for i, d in delays.items() if 0 <= d <= WINDOW_H}
    nonneg = [d for d in delays.values() if d >= 0]
    return {
        "created": datetime.fromtimestamp(t0, UTC),
        "tags": sorted(item.get("tags", [])),
        "n_answers_7d": len(in_win),
        "first_answer_hours": min(nonneg) if nonneg else None,
        "accepted_7d": any(a["is_accepted"] and a["answer_id"] in in_win for a in answers),
        "answer_count_now": item.get("answer_count", 0),
        "answer_ids_7d": in_win,
    }


def _plural(n: int) -> str:
    return f"{n} Antwort" if n == 1 else f"{n} Antworten"


def _fmt(v) -> str:
    if v is None:
        return "–"
    if isinstance(v, bool):
        return "ja" if v else "nein"
    if isinstance(v, datetime):
        return v.strftime("%d.%m.%Y %H:%M:%S")
    if isinstance(v, float):
        return f"{v:.2f}".replace(".", ",")
    if isinstance(v, list):
        return " ".join(v)
    return str(v)


def compare_question(stored: dict, api: dict | None) -> list[dict]:
    """Je Feld: gespeicherter Wert, heutiger API-Wert, gleich?, Erklärung der Abweichung."""
    keys = ("created", "tags", "n_answers_7d", "first_answer_hours", "accepted_7d",
            "answer_count_now")  # fmt: skip
    if api is None:
        why = "Frage seit dem Abruf gelöscht oder nicht mehr öffentlich (API liefert sie nicht)"
        return [
            {
                "feld": f,
                "gespeichert": _fmt(stored[k]),
                "api": "–",
                "gleich": False,
                "erklaerung": why,
            }  # fmt: skip
            for f, k in zip(FIELDS, keys, strict=True)
        ]
    gone = stored["answer_ids_7d"] - api["answer_ids_7d"]
    new = api["answer_ids_7d"] - stored["answer_ids_7d"]
    rows = []
    for f, k in zip(FIELDS, keys, strict=True):
        a, b = stored[k], api[k]
        floats = isinstance(a, float) and isinstance(b, float)
        same = abs(a - b) < 1e-6 if floats else a == b
        why = ""
        if not same:
            if k == "created":
                why = "nicht erklärbar"
            elif k == "tags":
                why = "Tags seit dem Abruf bearbeitet"
                if (set(a) - set(b)) & config.NEW_TYPE_TAGS:
                    why = "Tag des neuen Fragetyps fehlt heute (bearbeitet oder Typ umgestellt)"
            elif k == "n_answers_7d":
                parts = []
                if gone:
                    parts.append(f"{_plural(len(gone))} im Fenster seit dem Abruf gelöscht")
                if new:
                    parts.append(
                        f"{_plural(len(new))} im Fenster neu sichtbar (z. B. wiederhergestellt)"
                    )  # noqa: E501
                why = "; ".join(parts) or "nicht erklärbar"
            elif k == "first_answer_hours":
                if b is None or (a is not None and b > a):
                    why = "früheste gespeicherte Antwort heute nicht mehr sichtbar (gelöscht)"
                else:
                    why = "frühere Antwort heute sichtbar (z. B. wiederhergestellt)"
            elif k == "accepted_7d":
                why = "Akzeptanz seit dem Abruf geändert (zurückgenommen oder neu vergeben)"
                if gone:
                    why = "Akzeptanz geändert: akzeptierte Antwort seit dem Abruf gelöscht"
            elif k == "answer_count_now":
                why = "heutiger Wert, seit dem Abruf verändert; geht in keine Kennzahl ein"
        rows.append({"feld": f, "gespeichert": _fmt(a), "api": _fmt(b), "gleich": same,
                     "erklaerung": why})  # fmt: skip
    return rows


def fetch(ids: list[int]) -> dict:
    """Fragen und ihre Antworten heute über die API (zwischengespeichert, ohne Nutzerangaben)."""
    ids = sorted(ids)
    if CACHE.exists():
        cached = json.loads(CACHE.read_text(encoding="utf-8"))
        if cached.get("ids") == ids:
            return cached
    from sov.se_client import _api  # noqa: PLC0415

    api = _api()
    vec = ";".join(map(str, ids))
    qs = api.get(f"questions/{vec}", pagesize=100).get("items", [])
    answers, page = [], 1
    while True:
        data = api.get(f"questions/{vec}/answers", page=page, pagesize=100)
        answers += data.get("items", [])
        if not data.get("has_more"):
            break
        page += 1
        time.sleep(0.2)
    keep_q = ("question_id", "creation_date", "tags", "answer_count", "accepted_answer_id")
    keep_a = ("answer_id", "question_id", "creation_date", "is_accepted")
    out = {
        "ids": ids,
        "abgerufen": datetime.now(UTC).isoformat(timespec="seconds"),
        "questions": [{k: it.get(k) for k in keep_q} for it in qs],
        "answers": [{k: it.get(k) for k in keep_a} for it in answers],
    }
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def owner_hash(user_id: int | None) -> str | None:
    """Konto nur als Hash vergleichen; Nutzer-IDs werden nie gespeichert oder ausgegeben."""
    if user_id is None:
        return None
    return hashlib.sha256(f"sov-{user_id}".encode()).hexdigest()[:16]


def draw_check_answers(a: pl.DataFrame, n: int, seed: int) -> list[int]:
    """n zufällige Antworten aus dem 7-Tage-Fenster (erwartet answer_id, in_window)."""
    ids = sorted(a.filter(pl.col("in_window"))["answer_id"].to_list())
    rng = np.random.default_rng(seed)
    return sorted(int(i) for i in rng.choice(ids, n, replace=False))


def compare_answer(stored: dict, api: dict | None) -> dict:
    """Antwort heute vorhanden? Frage, Erstellzeit, Konto (als Hash) und Akzeptanz gleich?"""
    if api is None:
        keys = ("gleich", "frage_gleich", "zeit_gleich", "konto_gleich", "akzeptiert_gleich")
        why = "Antwort seit dem Abruf gelöscht (API liefert sie nicht)"
        return {**dict.fromkeys(keys, False), "erklaerung": why}
    res = {
        "frage_gleich": api["question_id"] == stored["question_id"],
        "zeit_gleich": datetime.fromtimestamp(api["creation_date"], UTC) == stored["created"],
        "konto_gleich": api["owner"] == stored["owner"],
        "akzeptiert_gleich": bool(api["is_accepted"]) == bool(stored["is_accepted"]),
    }
    why = []
    if not res["konto_gleich"]:
        why.append(
            "Konto seit dem Abruf gelöscht" if api["owner"] is None else "Konto nicht erklärbar"
        )
    if not res["akzeptiert_gleich"]:
        why.append("Akzeptanz seit dem Abruf geändert")
    if not (res["frage_gleich"] and res["zeit_gleich"]):
        why.append("Frage oder Erstellzeit nicht erklärbar")
    return {"gleich": all(res.values()), **res, "erklaerung": "; ".join(why)}


def fetch_answers(ids: list[int]) -> dict:
    """Antworten heute über die API (zwischengespeichert; Konto nur als Hash)."""
    ids = sorted(ids)
    if CACHE_A.exists():
        cached = json.loads(CACHE_A.read_text(encoding="utf-8"))
        if cached.get("ids") == ids:
            return cached
    from sov.se_client import _api  # noqa: PLC0415

    items = _api().get(f"answers/{';'.join(map(str, ids))}", pagesize=100).get("items", [])
    out = {
        "ids": ids,
        "abgerufen": datetime.now(UTC).isoformat(timespec="seconds"),
        "answers": [
            {
                "answer_id": it["answer_id"],
                "question_id": it["question_id"],
                "creation_date": it["creation_date"],
                "is_accepted": it.get("is_accepted", False),
                "owner": owner_hash((it.get("owner") or {}).get("user_id")),
            }  # fmt: skip
            for it in items
        ],
    }
    CACHE_A.parent.mkdir(parents=True, exist_ok=True)
    CACHE_A.write_text(json.dumps(out), encoding="utf-8")
    return out
