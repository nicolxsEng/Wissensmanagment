"""Menschliche Prüfung der Modell-Kodierung (D29): blinde Stichproben und Auswertung.

Die Autor:innen ordnen Tags und Fragen selbst ein, ohne die Einordnung der Modelle zu sehen.
Verglichen wird danach mit dem Konsens der beiden Modelle (Referenz der Gruppen bzw. von AP10).
"""

import math

import numpy as np

from sov import config
from sov.agreement import kappa_ci


def stratified_tags(groups: dict[str, list[str]], n: int, seed: int) -> list[str]:
    """Stichprobe aus den Gruppen G und U: die kleinere Gruppe ganz (höchstens n // 2 Tags),
    der Rest zufällig aus der größeren. Sortiert zurück; die Reihenfolge mischt der Bogen."""
    small, large = sorted(("G", "U"), key=lambda g: (len(groups[g]), g))
    rng = np.random.default_rng(seed)
    s = sorted(groups[small])
    if len(s) > n // 2:
        s = sorted(rng.choice(s, n // 2, replace=False).tolist())
    rest = sorted(rng.choice(sorted(groups[large]), n - len(s), replace=False).tolist())
    return sorted(s + rest)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def compare(human: list[str], ref: list[str], labels: list[str]) -> dict:
    """Kappa Mensch–Referenz und Übereinstimmung je Referenzklasse (mit Wilson-Intervall)."""
    out = kappa_ci(human, ref, labels)
    per = {}
    for lab in labels:
        idx = [i for i, r in enumerate(ref) if r == lab]
        if idx:
            k = sum(human[i] == lab for i in idx)
            lo, hi = wilson(k, len(idx))
            per[lab] = {"k": k, "n": len(idx), "anteil": k / len(idx), "ci_low": lo, "ci_high": hi}
    return {**out, "je_klasse": per}


def tags_confirmed(res: dict, groups: tuple[str, ...] = ("G", "U")) -> bool:
    """D29: κ ≥ KAPPA_MIN und in jeder Gruppe ≥ PRUEF_GRUPPE_MIN gleich eingeordnet."""
    return res["kappa"] >= config.KAPPA_MIN and all(
        res["je_klasse"][g]["anteil"] >= config.PRUEF_GRUPPE_MIN for g in groups
    )


def questions_confirmed(res: dict) -> bool:
    """D29: κ Mensch–Konsens ≥ KAPPA_MIN."""
    return res["kappa"] >= config.KAPPA_MIN
