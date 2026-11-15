"""AP06: Stichproben für die Kodierung von Fragetexten (plan.md AP06).

- Stichprobe: 50 klassische Fragen je Oktober 2015–2026 (600)
- davon doppelt kodiert: 150, geschichtet (je Jahr 12 oder 13) -> Testmenge für AP10
- Kalibrierung: 30 Fragen aus denselben Jahren, nicht in der Stichprobe
- Codes F001…F630 in zufälliger Reihenfolge, damit sie das Jahr nicht verraten
"""

import polars as pl

from sov import config


def draw_samples(q: pl.DataFrame, seed: int = config.SEED) -> pl.DataFrame:
    """q: question_id, year, is_classic. Rückgabe: code, question_id, year, set, doppelt, split."""
    pool = (
        q.filter(pl.col("is_classic") & pl.col("year").is_in(config.SAMPLE_YEARS))
        .select("question_id", "year")
        .sort("question_id")
    )
    main_parts, rest_parts = [], []
    for y in config.SAMPLE_YEARS:
        sub = pool.filter(pl.col("year") == y)
        picked = sub.sample(config.SAMPLE_PER_YEAR, seed=seed + y, shuffle=True)
        main_parts.append(picked)
        rest_parts.append(sub.filter(~pl.col("question_id").is_in(picked["question_id"].to_list())))
    main = pl.concat(main_parts)

    # Kalibrierung: je Jahr 3 Kandidaten, davon 30 zufällig
    cal_pool = pl.concat(
        [r.sample(3, seed=seed + 1000 + i, shuffle=True) for i, r in enumerate(rest_parts)]
    )
    cal = cal_pool.sample(config.CALIBRATION_N, seed=seed + 2000, shuffle=True)

    # Doppelkodierung: 150 geschichtet; welche Jahre 13 statt 12 bekommen, entscheidet der Zufall
    n_years = len(config.SAMPLE_YEARS)
    base, extra = divmod(config.DOUBLE_CODED_N, n_years)
    years_extra = set(
        pl.Series(config.SAMPLE_YEARS).sample(extra, seed=seed + 3000, shuffle=True).to_list()
    )
    dbl_ids = []
    for y in config.SAMPLE_YEARS:
        k = base + (1 if y in years_extra else 0)
        sub = main.filter(pl.col("year") == y).sort("question_id")
        dbl_ids += sub.sample(k, seed=seed + 4000 + y, shuffle=True)["question_id"].to_list()

    main = main.with_columns(
        set=pl.lit("stichprobe"), doppelt=pl.col("question_id").is_in(dbl_ids)
    ).with_columns(split=pl.when(pl.col("doppelt")).then(pl.lit("test")).otherwise(pl.lit("train")))
    cal = cal.with_columns(
        set=pl.lit("kalibrierung"), doppelt=pl.lit(False), split=pl.lit(None, pl.String)
    )
    allq = pl.concat([main, cal]).sort("question_id")
    allq = allq.sample(fraction=1.0, seed=seed + 5000, shuffle=True)
    allq = allq.with_columns(
        code=pl.format("F{}", pl.int_range(1, allq.height + 1).cast(pl.String).str.zfill(3))
    )
    return allq.select("code", "question_id", "year", "set", "doppelt", "split").sort("code")
