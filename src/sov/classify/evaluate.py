"""AP10: Bewertung (Macro-F1 mit Bootstrap-KI), Kreuzvalidierung und Sperre der Testmenge."""

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold

from sov import config

LABELS = list(config.QUESTION_CATEGORIES)


def macro_f1_ci(
    y_true: list[str], y_pred: list[str], n_boot: int = 2000, seed: int = config.SEED
) -> dict:
    """Macro-F1 über G/U/S mit 95-%-Bootstrap-Intervall und F1 je Klasse."""
    yt, yp = np.asarray(y_true), np.asarray(y_pred)
    f1 = f1_score(yt, yp, labels=LABELS, average="macro", zero_division=0)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        i = rng.integers(0, len(yt), len(yt))
        boots.append(f1_score(yt[i], yp[i], labels=LABELS, average="macro", zero_division=0))
    per_class = f1_score(yt, yp, labels=LABELS, average=None, zero_division=0)
    return {
        "macro_f1": float(f1),
        "ci_low": float(np.quantile(boots, 0.025)),
        "ci_high": float(np.quantile(boots, 0.975)),
        "accuracy": float(np.mean(yt == yp)),
        **{f"f1_{lab}": float(v) for lab, v in zip(LABELS, per_class, strict=True)},
        "n": int(len(yt)),
    }


def confusion(y_true: list[str], y_pred: list[str]) -> list[list[int]]:
    return confusion_matrix(y_true, y_pred, labels=LABELS).tolist()


def cross_validate(
    make_model: Callable[[], object], texts: list[str], labels: list[str], k: int = 5,
    seed: int = config.SEED,
) -> dict:  # fmt: skip
    """k-fache Kreuzvalidierung NUR auf den Trainingsfragen (Auswahl von Einstellungen)."""
    t, y = np.asarray(texts, dtype=object), np.asarray(labels)
    preds = np.empty(len(y), dtype=object)
    for tr, te in StratifiedKFold(n_splits=k, shuffle=True, random_state=seed).split(t, y):
        m = make_model().fit(list(t[tr]), list(y[tr]))
        preds[te] = m.predict(list(t[te]))
    return macro_f1_ci(list(y), list(preds), seed=seed)


class HoldoutLock:
    """Jeder Kandidat darf genau einmal auf der Testmenge ausgewertet werden (D06).

    Der Eintrag wird geschrieben, BEVOR die Vorhersagen mit den Testlabels verglichen werden.
    """

    def __init__(self, path: Path | None = None):
        self.path = path or (config.RESULTS_DIR / "classify" / "testlaeufe.json")

    def _load(self) -> dict:
        return json.loads(self.path.read_text()) if self.path.exists() else {}

    def claim(self, candidate: str, note: str = "") -> None:
        runs = self._load()
        if candidate in runs:
            raise PermissionError(
                f"Kandidat '{candidate}' wurde am {runs[candidate]['datum']} schon auf der "
                "Testmenge ausgewertet. Eine zweite Auswertung ist nicht erlaubt (D06)."
            )
        runs[candidate] = {"datum": datetime.now().isoformat(timespec="seconds"), "notiz": note}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(runs, indent=2, ensure_ascii=False))
