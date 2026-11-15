"""AP10: Eingabetexte für die Klassifikation und Anwendungsstichprobe.

Eingabe je Frage: Titel + Fließtext mit [CODE]-Platzhaltern + Auszug aus dem Code, gekürzt.
Keine Tags, kein Jahr, kein Score (gleiche Information wie in der Kodier-App, D05/D18).
"""

import polars as pl

from sov import config

CODE_EXCERPT_CHARS = 600


def model_input(
    title: str, body_text: str, body_code: str, max_chars: int = config.CODING_VIEW_MAX_CHARS
) -> str:
    """Text, den alle Verfahren sehen."""
    s = f"{title}\n\n{body_text}".strip()
    if body_code and body_code.strip():
        s += "\n\nCode (Auszug): " + body_code.strip()[:CODE_EXCERPT_CHARS]
    return s[:max_chars]


def with_inputs(df: pl.DataFrame) -> pl.DataFrame:
    """Ergänzt eine Spalte `text` aus title, body_text, body_code."""
    texts = [
        model_input(t, b or "", c or "")
        for t, b, c in zip(df["title"], df["body_text"], df["body_code"], strict=True)
    ]
    return df.with_columns(text=pl.Series(texts))


def application_sample(
    q: pl.DataFrame, exclude_ids: set[int], seed: int = config.SEED
) -> pl.DataFrame:
    """2.000 klassische Fragen je Oktober 2015–2025, 2026 alle; ohne die kodierten Fragen."""
    parts = []
    for y in config.SAMPLE_YEARS:
        sub = (
            q.filter(pl.col("is_classic") & (pl.col("year") == y))
            .filter(~pl.col("question_id").is_in(list(exclude_ids)))
            .select("question_id", "year")
            .sort("question_id")
        )
        n = min(config.CLASSIFY_PER_YEAR, sub.height)
        parts.append(sub.sample(n, seed=seed + 100 + y, shuffle=True))
    return pl.concat(parts)


def coded_texts(codes_csv: str | None = None) -> pl.DataFrame:
    """Eingabetexte der 630 kodierten Fragen (Code, Split, Text) – ohne Labels."""
    from sov.io import load_texts  # noqa: PLC0415

    path = codes_csv or (config.CODING_DIR / "questions" / "stichprobe_intern.csv")
    s = pl.read_csv(path).select("code", "question_id", "set", "split")
    t = load_texts().filter(pl.col("question_id").is_in(s["question_id"].to_list())).collect()
    return with_inputs(s.join(t, on="question_id")).select("code", "set", "split", "text")
