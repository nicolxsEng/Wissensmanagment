"""AP08: Unterbrochene Zeitreihe nach Bernal et al. (2017), plan.md 5.5.

Zwei Auswertungen je Reihe (Oktober 2015–2026):

1. Fortschreibung (Hauptauswertung): lineares Modell nur auf 2015–2022, auf Log-Skala
   (Zählungen, Wartezeiten, Längen) bzw. Logit-Skala (Anteile). Fortschreibung auf 2023–2026
   mit 95-%-Vorhersageintervall; berichtet wird beobachtet / erwartet − 1.
2. Segmentierte Regression (Ergänzung): y = β0 + β1·t + β2·nach + β3·s·nach mit t = Jahr − 2022,
   s = Jahr − 2023
   über alle Jahre ab 2015. β2 = Niveausprung in 2023, β3 = Änderung der Steigung (nur 12
   Punkte, Autokorrelation nicht modellierbar).

Die Funktionen nehmen einfache Listen, damit AP07 (Gruppenanteile) und AP14 sie wiederverwenden.
"""

import math
from collections.abc import Sequence

import numpy as np
import statsmodels.api as sm

from sov import config

# TF1-Kennzahlen und ihre Skala (plan.md 5.3; Median der Antworten je Frage ist fast
# immer 1 und wird deshalb nicht modelliert)
TF1_METRICS: dict[str, str] = {
    "n_questions": "log",
    "answers_per_q_mean": "log",
    "unanswered_share": "logit",
    "first_answer_median_h": "log",
    "answered_24h_share": "logit",
    "accepted_share": "logit",
    "body_len_median": "log",
}

TERMS = ("konstante", "trend", "niveau", "steigung")


def logit(p: float) -> float:
    return math.log(p / (1 - p))


def expit(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def transform(values: Sequence[float], scale: str) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    if scale == "log":
        return np.log(v)
    if scale == "logit":
        return np.log(v / (1 - v))
    if scale == "linear":
        return v
    raise ValueError(scale)


def back(x: np.ndarray, scale: str) -> np.ndarray:
    if scale == "log":
        return np.exp(x)
    if scale == "logit":
        return 1 / (1 + np.exp(-x))
    return x


def _select(years: Sequence[int], values: Sequence[float], start: int):
    pairs = [(y, v) for y, v in zip(years, values, strict=True) if y >= start]
    ys = np.array([p[0] for p in pairs], dtype=float)
    vs = np.array([p[1] for p in pairs], dtype=float)
    return ys, vs


def fit_pretrend(
    years: Sequence[int],
    values: Sequence[float],
    scale: str,
    start: int = config.TREND_START,
    cut: int = config.BASE_YEAR,
    alpha: float = 0.05,
) -> list[dict]:
    """Trend auf start..cut schätzen und fortschreiben. Eine Zeile je Jahr ab start."""
    ys, vs = _select(years, values, start)
    t = ys - cut
    pre = ys <= cut
    model = sm.OLS(transform(vs[pre], scale), sm.add_constant(t[pre])).fit()
    frame = model.get_prediction(sm.add_constant(t)).summary_frame(alpha=alpha)
    exp_ = back(frame["mean"].to_numpy(), scale)
    lo = back(frame["obs_ci_lower"].to_numpy(), scale)
    hi = back(frame["obs_ci_upper"].to_numpy(), scale)
    rows = []
    for i, y in enumerate(ys.astype(int)):
        obs = vs[i]
        outside = ""
        if y > cut:
            outside = "darunter" if obs < lo[i] else ("darüber" if obs > hi[i] else "")
        rows.append(
            {
                "year": int(y),
                "is_pre": bool(pre[i]),
                "observed": float(obs),
                "expected": float(exp_[i]),
                "pi_low": float(lo[i]),
                "pi_high": float(hi[i]),
                "deviation_pct": float((obs / exp_[i] - 1) * 100),
                "outside_pi": outside,
            }
        )
    return rows


def segmented(
    years: Sequence[int],
    values: Sequence[float],
    scale: str,
    start: int = config.TREND_START,
    cut: int = config.BASE_YEAR,
    alpha: float = 0.05,
) -> list[dict]:
    """Segmentierte Regression; je Term Koeffizient mit KI und Effekt auf natürlicher Skala.

    effect: bei Log-Skala Faktor (exp β), bei Logit-Skala Odds Ratio (exp β).
    """
    ys, vs = _select(years, values, start)
    t = ys - cut
    post = (ys > cut).astype(float)
    # Zeit seit dem ersten Jahr nach dem Schnitt (2023 = 0): β2 ist dann der Sprung in 2023
    # gegenüber dem fortgeschriebenen Trend, nicht ein Wert der rückwärts verlängerten Geraden.
    t_since = (ys - (cut + 1)) * post
    x = np.column_stack([np.ones_like(t), t, post, t_since])
    model = sm.OLS(transform(vs, scale), x).fit()
    ci = model.conf_int(alpha=alpha)
    rows = []
    for j, term in enumerate(TERMS):
        coef, low, high = float(model.params[j]), float(ci[j][0]), float(ci[j][1])
        eff = (lambda b: math.exp(b)) if scale in ("log", "logit") else (lambda b: b)
        rows.append(
            {
                "term": term,
                "coef": coef,
                "ci_low": low,
                "ci_high": high,
                "effect": eff(coef),
                "effect_low": eff(low),
                "effect_high": eff(high),
                "n_points": int(len(ys)),
            }
        )
    return rows
