"""Übereinstimmung zweier Kodierinstanzen: Cohens Kappa mit Bootstrap-KI, Kreuztabelle."""

import numpy as np
import polars as pl
from sklearn.metrics import cohen_kappa_score

from sov import config


def kappa_ci(
    a: list[str], b: list[str], labels: list[str], n_boot: int = 2000, seed: int = config.SEED
) -> dict:
    """Cohens Kappa, 95-%-Bootstrap-Intervall und Übereinstimmung in Prozent."""
    x, y = np.asarray(a), np.asarray(b)
    k = cohen_kappa_score(x, y, labels=labels)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        i = rng.integers(0, len(x), len(x))
        if len(set(x[i]) | set(y[i])) > 1:
            boots.append(cohen_kappa_score(x[i], y[i], labels=labels))
    return {
        "kappa": float(k),
        "ci_low": float(np.quantile(boots, 0.025)),
        "ci_high": float(np.quantile(boots, 0.975)),
        "uebereinstimmung": float(np.mean(x == y)),
        "n": int(len(x)),
    }


def crosstab(a: list[str], b: list[str], labels: list[str], name_a: str, name_b: str):
    """Kreuztabelle als DataFrame: Zeilen = a, Spalten = b."""
    df = pl.DataFrame({name_a: a, name_b: b})
    rows = []
    for la in labels:
        row = {name_a: la}
        for lb in labels:
            row[lb] = df.filter((pl.col(name_a) == la) & (pl.col(name_b) == lb)).height
        rows.append(row)
    return pl.DataFrame(rows)


def landis_koch(k: float) -> str:
    """Einordnung nach Landis & Koch (1977)."""
    for bound, text in ((0.0, "schlecht"), (0.2, "gering"), (0.4, "ausreichend"),
                        (0.6, "mittelmäßig"), (0.8, "substanziell")):  # fmt: skip
        if k <= bound:
            return text
    return "fast vollkommen"
