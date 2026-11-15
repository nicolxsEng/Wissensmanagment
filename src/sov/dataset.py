"""AP01: Rohdaten -> data/interim/{questions,answers,texts}.parquet.

Je Jahr wird ein Teil nach data/interim/_parts/ geschrieben (Zwischenspeicher, wird bei
erneutem Lauf wiederverwendet). Danach werden die Teile zu den drei Tabellen
zusammengefügt. Spalten: docs/datenmodell.md, Definitionen: plan.md Abschnitt 5.
"""

import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from sov import config
from sov.io import iter_jsonl_gz, raw_year_dir, read_progress
from sov.text import clean_title, split_body

PARTS_DIR = config.INTERIM_DIR / "_parts"
WINDOW_H = float(config.ANSWER_WINDOW_HOURS)
FAST_H = float(config.FAST_ANSWER_HOURS)

# Median der Textlänge ohne Code laut Projektstand vom 14.11.2026 (alle Fragen)
PROJEKTSTAND_MEDIAN_LEN = {
    2008: 422, 2009: 407, 2010: 398, 2011: 416, 2012: 427, 2013: 417, 2014: 426,
    2015: 418, 2016: 418, 2017: 422, 2018: 425, 2019: 437, 2020: 427, 2021: 422,
    2022: 426, 2023: 510, 2024: 588, 2025: 656, 2026: 719,
}  # fmt: skip


# ----------------------------------------------------------------------------- Antwortfenster
def add_answer_features(
    q: pl.DataFrame, a: pl.DataFrame
) -> tuple[pl.DataFrame, pl.DataFrame, dict[str, int]]:
    """Berechnet Antwortfenster-Felder (plan.md 5.2).

    q braucht question_id, created_ts (Unix-Sekunden); a braucht answer_id, question_id,
    created_ts, is_accepted. Gibt (q mit Feldern, a mit delay_hours/in_window, Zähler) zurück.
    """
    a = a.join(
        q.select("question_id", pl.col("created_ts").alias("_q_ts")),
        on="question_id",
        how="left",
    ).with_columns(delay_hours=(pl.col("created_ts") - pl.col("_q_ts")) / 3600.0)
    a = a.with_columns(
        in_window=pl.col("delay_hours").is_between(0.0, WINDOW_H).fill_null(False)
    ).drop("_q_ts")

    stats = {
        "orphan_answers": int(a["delay_hours"].is_null().sum()),
        "negative_delay": int((a["delay_hours"] < 0).sum()),
    }

    per_q = (
        a.filter(pl.col("delay_hours") >= 0)
        .group_by("question_id")
        .agg(
            n_answers_7d=pl.col("in_window").sum().cast(pl.Int16),
            first_answer_hours=pl.col("delay_hours").min(),
            accepted_7d=(pl.col("is_accepted") & pl.col("in_window")).any(),
        )
    )
    q = q.join(per_q, on="question_id", how="left").with_columns(
        n_answers_7d=pl.col("n_answers_7d").fill_null(0).cast(pl.Int16),
        accepted_7d=pl.col("accepted_7d").fill_null(False),
    )
    q = q.with_columns(
        answered_7d=pl.col("n_answers_7d") > 0,
        answered_24h=(pl.col("first_answer_hours") <= FAST_H).fill_null(False),
    )
    return q, a, stats


# ----------------------------------------------------------------------------- ein Jahr
def _owner_id(rec: dict) -> int | None:
    owner = rec.get("owner") or {}
    return owner.get("user_id")


def _parse_questions(year: int) -> tuple[pl.DataFrame, pl.DataFrame]:
    cols: dict[str, list] = {k: [] for k in (
        "question_id", "created_ts", "title", "tags", "score", "view_count",
        "answer_count_now", "accepted_answer_id", "closed_reason", "owner_user_id",
        "body_len_nocode", "n_code_blocks", "code_chars", "body_text", "body_code",
        "body_empty",
    )}  # fmt: skip
    for r in iter_jsonl_gz(raw_year_dir(year) / "questions.jsonl.gz"):
        body = r.get("body") or ""
        parts = split_body(body)
        cols["question_id"].append(r["question_id"])
        cols["created_ts"].append(r["creation_date"])
        cols["title"].append(clean_title(r.get("title")))
        cols["tags"].append(r.get("tags") or [])
        cols["score"].append(r.get("score"))
        cols["view_count"].append(r.get("view_count"))
        cols["answer_count_now"].append(r.get("answer_count"))
        cols["accepted_answer_id"].append(r.get("accepted_answer_id"))
        cols["closed_reason"].append(r.get("closed_reason") if "closed_date" in r else None)
        cols["owner_user_id"].append(_owner_id(r))
        cols["body_len_nocode"].append(parts.len_nocode)
        cols["n_code_blocks"].append(parts.n_code_blocks)
        cols["code_chars"].append(parts.code_chars)
        cols["body_text"].append(parts.text_for_model)
        cols["body_code"].append(parts.code)
        cols["body_empty"].append(not body.strip())
    df = pl.DataFrame(
        cols,
        schema_overrides={
            "tags": pl.List(pl.String),
            "accepted_answer_id": pl.Int64,
            "owner_user_id": pl.Int64,
            "closed_reason": pl.String,
        },
    )
    texts = df.select(
        "question_id", pl.lit(year, pl.Int16).alias("year"), "title", "body_text", "body_code"
    )
    return df.drop("body_text", "body_code"), texts


def _parse_answers(year: int) -> pl.DataFrame:
    cols: dict[str, list] = {
        k: [] for k in ("answer_id", "question_id", "created_ts", "score", "is_accepted",
                        "owner_user_id")
    }  # fmt: skip
    for r in iter_jsonl_gz(raw_year_dir(year) / "answers.jsonl.gz"):
        cols["answer_id"].append(r["answer_id"])
        cols["question_id"].append(r["question_id"])
        cols["created_ts"].append(r["creation_date"])
        cols["score"].append(r.get("score"))
        cols["is_accepted"].append(bool(r.get("is_accepted")))
        cols["owner_user_id"].append(_owner_id(r))
    return pl.DataFrame(cols, schema_overrides={"owner_user_id": pl.Int64})


def _to_datetime(col: str) -> pl.Expr:
    return pl.from_epoch(pl.col(col), time_unit="s").dt.replace_time_zone("UTC")


def build_year(year: int, force: bool = False) -> dict:
    """Baut die Teiltabellen eines Jahres und gibt Kennzahlen fürs Datenprotokoll zurück."""
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    paths = {k: PARTS_DIR / f"{k}_{year}.parquet" for k in ("questions", "answers", "texts")}
    stats_path = PARTS_DIR / f"stats_{year}.parquet"
    if not force and all(p.exists() for p in paths.values()) and stats_path.exists():
        return pl.read_parquet(stats_path).to_dicts()[0] | {"cached": True}

    t0 = time.perf_counter()
    q, texts = _parse_questions(year)
    a = _parse_answers(year)
    q, a, wstats = add_answer_features(q, a)

    start = int(datetime(year, config.MONTH, 1, tzinfo=UTC).timestamp())
    end = int(datetime(year, config.MONTH + 1, 1, tzinfo=UTC).timestamp())
    new_type_tags = sorted(config.NEW_TYPE_TAGS)
    ai_tags = sorted(config.AI_TAGS)

    q = q.with_columns(
        year=pl.lit(year, pl.Int16),
        created=_to_datetime("created_ts"),
        n_tags=pl.col("tags").list.len().cast(pl.Int8),
        is_closed=pl.col("closed_reason").is_not_null(),
        is_new_type=pl.col("tags").list.eval(pl.element().is_in(new_type_tags)).list.any()
        & (pl.col("created_ts") >= int(config.NEW_TYPE_START.timestamp())),
        n_ai_tags=pl.col("tags").list.eval(pl.element().is_in(ai_tags)).list.sum().cast(pl.Int8),
        has_code=pl.col("n_code_blocks") > 0,
        out_of_month=~pl.col("created_ts").is_between(start, end, closed="left"),
    ).with_columns(is_classic=~pl.col("is_new_type"))

    q_out = q.select(
        "question_id", "year", "created", "title", "tags", "n_tags",
        pl.col("score").cast(pl.Int32), pl.col("view_count").cast(pl.Int64),
        pl.col("answer_count_now").cast(pl.Int32), "accepted_answer_id",
        "is_closed", "closed_reason", "is_new_type", "is_classic", "n_ai_tags",
        pl.col("body_len_nocode").cast(pl.Int32), "has_code",
        pl.col("n_code_blocks").cast(pl.Int16), pl.col("code_chars").cast(pl.Int32),
        "n_answers_7d", "first_answer_hours", "answered_7d", "answered_24h", "accepted_7d",
        "owner_user_id",
    ).sort("created", "question_id")  # fmt: skip
    a_out = a.select(
        "answer_id", "question_id", pl.lit(year, pl.Int16).alias("year"),
        _to_datetime("created_ts").alias("created"), "delay_hours", "in_window",
        pl.col("score").cast(pl.Int32), "is_accepted", "owner_user_id",
    ).sort("question_id", "created")  # fmt: skip

    q_out.write_parquet(paths["questions"], compression="zstd")
    a_out.write_parquet(paths["answers"], compression="zstd")
    texts.write_parquet(paths["texts"], compression="zstd")

    # Kontrolle: akzeptierte Antwort laut Frage, aber im Datensatz nicht als akzeptiert markiert
    acc_ids = set(a.filter(pl.col("is_accepted"))["answer_id"].to_list())
    acc_q = q.filter(pl.col("accepted_answer_id").is_not_null())["accepted_answer_id"]
    progress = read_progress(year)
    stats = {
        "year": year,
        "questions": q.height,
        "questions_expected": progress.get("questions"),
        "answers": a.height,
        "answers_expected": progress.get("answers"),
        "orphan_answers": wstats["orphan_answers"],
        "negative_delay": wstats["negative_delay"],
        "answers_without_owner": int(a["owner_user_id"].is_null().sum()),
        "answers_in_window": int(a["in_window"].sum()),
        "empty_bodies": int(q["body_empty"].sum()),
        "out_of_month": int(q["out_of_month"].sum()),
        "accepted_not_found": int((~acc_q.is_in(list(acc_ids))).sum()),
        "new_type": int(q["is_new_type"].sum()),
        "median_len_all": float(q["body_len_nocode"].median()),
        "median_len_classic": float(q.filter(pl.col("is_classic"))["body_len_nocode"].median()),
        "seconds": round(time.perf_counter() - t0, 1),
    }
    pl.DataFrame([stats]).write_parquet(stats_path)
    return stats | {"cached": False}


# ----------------------------------------------------------------------------- alle Jahre
def _combine(kind: str, years: list[int], target: Path) -> None:
    parts = [PARTS_DIR / f"{kind}_{y}.parquet" for y in years]
    pl.scan_parquet(parts).sink_parquet(target, compression="zstd")


def build_all(
    years: list[int] | None = None, workers: int = 8, force: bool = False, log=print
) -> list[dict]:
    """Baut alle (oder die genannten) Jahre und fügt danach alle vorhandenen Teile zusammen."""
    years = years or config.YEARS
    # große Jahre zuerst, damit die Prozesse gleichmäßig ausgelastet sind
    order = sorted(years, key=lambda y: -(raw_year_dir(y) / "questions.jsonl.gz").stat().st_size)
    results: dict[int, dict] = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(build_year, y, force): y for y in order}
        for fut in as_completed(futures):
            s = fut.result()
            results[s["year"]] = s
            tag = "Zwischenspeicher" if s.get("cached") else f"{s['seconds']} s"
            log(f"  {s['year']}: {s['questions']:>7,} Fragen, {s['answers']:>7,} Antworten ({tag})")

    available = [y for y in config.YEARS if (PARTS_DIR / f"questions_{y}.parquet").exists()]
    if available == config.YEARS:
        log("Füge alle 19 Jahre zusammen …")
        _combine("questions", available, config.QUESTIONS_PARQUET)
        _combine("answers", available, config.ANSWERS_PARQUET)
        _combine("texts", available, config.TEXTS_PARQUET)
    else:
        missing = sorted(set(config.YEARS) - set(available))
        log(f"Noch nicht alle Jahre gebaut (fehlen: {missing}) – Gesamttabellen nicht erzeugt.")
    return [results[y] for y in sorted(results)]
