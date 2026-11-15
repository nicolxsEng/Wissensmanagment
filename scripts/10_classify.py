"""AP10: Automatische Einordnung von Fragetexten (G/U/S) mit lokalen Modellen.

uv sync --group topics --group ml                     # einmalig
uv run python scripts/10_classify.py prepare          # Eingabetexte (kodiert + Anwendung)
uv run python scripts/10_classify.py benchmark        # Laufzeit messen (ohne Labels)
--- ab hier werden die Labels aus AP09 gebraucht (coding/questions/labels_600.csv) ---
uv run python scripts/10_classify.py select    # Kreuzvalidierung NUR auf 450 Trainingsfragen
uv run python scripts/10_classify.py test      # jeder Kandidat GENAU EINMAL auf 150 Testfragen
uv run python scripts/10_classify.py apply            # Gewinner auf ~22.900 Fragen anwenden

Umgebungsvariablen (nur für Tests): SOV_LABELS (Label-Datei), SOV_CLASSIFY_OUT (Ausgabeordner).
"""

import json
import os
import sys
import time
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

import numpy as np
import polars as pl

from sov import config
from sov.classify.candidates import (
    HYPOTHESES_V1,
    SetFitClassifier,
    TfidfLogReg,
    ZeroShotClassifier,
)
from sov.classify.data import application_sample, coded_texts, with_inputs
from sov.classify.evaluate import HoldoutLock, confusion, cross_validate, macro_f1_ci
from sov.io import load_questions, load_texts

OUT = Path(os.environ.get("SOV_CLASSIFY_OUT", config.RESULTS_DIR / "classify"))
LABELS = Path(os.environ.get("SOV_LABELS", config.CODING_DIR / "questions" / "labels_600.csv"))
CODED = config.PROCESSED_DIR / "classify_coded_inputs.parquet"
APPLY = config.PROCESSED_DIR / "classify_apply_inputs.parquet"
TFIDF_GRID = (0.5, 1.0, 2.0, 4.0)


def pkg_versions() -> dict:
    out = {}
    for p in ("scikit-learn", "setfit", "transformers", "sentence-transformers", "torch"):
        try:
            out[p] = version(p)
        except Exception:  # noqa: BLE001
            out[p] = "fehlt"
    return out


# ----------------------------------------------------------------------------- prepare
def prepare() -> None:
    coded = coded_texts()
    coded.write_parquet(CODED)
    q = load_questions(["question_id", "year", "is_classic"], canonical_tags=False)
    excl = set(
        pl.read_csv(config.CODING_DIR / "questions" / "stichprobe_intern.csv")["question_id"]
    )
    sample = application_sample(q, excl)
    t = load_texts().filter(pl.col("question_id").is_in(sample["question_id"].to_list())).collect()
    apply_df = with_inputs(sample.join(t.drop("year"), on="question_id")).select(
        "question_id", "year", "text"
    )
    apply_df.write_parquet(APPLY)
    print(f"Kodierte Fragen: {coded.height}, Anwendungsstichprobe: {apply_df.height} "
          f"({apply_df.group_by('year').len().sort('year')['len'].to_list()})")  # fmt: skip


# ----------------------------------------------------------------------------- benchmark
def benchmark(n: int = 200) -> None:
    """Laufzeit messen – ohne Labels, keine Aussage über Güte."""
    apply_df = pl.read_parquet(APPLY)
    texts = apply_df.sample(n, seed=config.SEED + 77)["text"].to_list()
    rows = []
    for model in (config.ZERO_SHOT_MODEL, config.ZERO_SHOT_MODEL_ALT):
        zs = ZeroShotClassifier(model_name=model).fit()
        zs.predict(texts[:8])  # Aufwärmen
        zs.predict(texts)
        per_q = zs.seconds / n
        rows.append({"verfahren": f"Zero-Shot {model.split('/')[-1]}", "s_je_frage": per_q,
                     "hochrechnung_anwendung_min": per_q * apply_df.height / 60})  # fmt: skip
    # SetFit: Probetraining mit Platzhalter-Labels (nur Zeitmessung!)
    coded = pl.read_parquet(CODED).filter(pl.col("set") == "stichprobe")
    tr = coded["text"].to_list()[:60]
    dummy = [("G", "U", "S")[i % 3] for i in range(len(tr))]
    t0 = time.perf_counter()
    sf = SetFitClassifier(num_iterations=5).fit(tr, dummy)
    t_train = time.perf_counter() - t0
    t0 = time.perf_counter()
    sf.predict(texts)
    per_q = (time.perf_counter() - t0) / n
    rows.append({"verfahren": "SetFit (Vorhersage)", "s_je_frage": per_q,
                 "hochrechnung_anwendung_min": per_q * apply_df.height / 60})  # fmt: skip
    # Hochrechnung Training: Paare wachsen linear mit Fragen × num_iterations
    t_train_full = t_train * (450 / 60) * (20 / 5)
    OUT.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Laufzeittest AP10 (ohne Labels)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. {n} zufällige Fragen der Anwendungsstichprobe "
        f"({apply_df.height} Fragen gesamt). Gerät: Apple-GPU (mps), falls verfügbar.",
        "",
        "| Verfahren | Sekunden je Frage | Hochrechnung Anwendung |",
        "|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['verfahren']} | {r['s_je_frage']:.3f} | "
                     f"{r['hochrechnung_anwendung_min']:.0f} min |")  # fmt: skip
    lines += [
        "",
        f"SetFit-Probetraining: 60 Fragen, 5 Iterationen in {t_train:.0f} s → "
        f"hochgerechnet auf 450 Fragen, 20 Iterationen: etwa {t_train_full / 60:.0f} min je "
        "Training (bei 5-facher Kreuzvalidierung × 5).",
        "",
        "Die Platzhalter-Labels dienen nur der Zeitmessung; dieser Lauf sagt nichts über Güte.",
        f"Pakete: {json.dumps(pkg_versions(), ensure_ascii=False)}",
    ]
    (OUT / "laufzeit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


# ----------------------------------------------------------------------------- mit Labels
def load_labeled(split: str) -> tuple[list[str], list[str]]:
    if not LABELS.exists():
        raise SystemExit(f"{LABELS} fehlt – zuerst AP09 (Kappa, Konsens, labels_600.csv).")
    lab = pl.read_csv(LABELS).select("code", "label")
    df = pl.read_parquet(CODED).filter(pl.col("split") == split).join(lab, on="code")
    return df["text"].to_list(), df["label"].to_list()


def candidates(best_c: float = 2.0) -> dict:
    return {
        "tfidf_logreg": lambda: TfidfLogReg(c=best_c),
        "setfit": lambda: SetFitClassifier(),
        "zero_shot": lambda: ZeroShotClassifier(),
    }


def select() -> None:
    """Einstellungen nur mit den 450 Trainingsfragen wählen (Testmenge bleibt unberührt)."""
    texts, labels = load_labeled("train")
    rows = []
    for c in TFIDF_GRID:
        r = cross_validate(lambda c=c: TfidfLogReg(c=c), texts, labels)
        rows.append({"kandidat": "tfidf_logreg", "einstellung": f"C={c}", **r})
    if os.environ.get("SOV_SETFIT_CV") == "1":  # optional, dauert mehrere Stunden
        rows.append({"kandidat": "setfit", "einstellung": "Standard",
                     **cross_validate(SetFitClassifier, texts, labels)})  # fmt: skip
    if os.environ.get("SOV_SKIP_SLOW") != "1":
        zs = ZeroShotClassifier().fit()
        rows.append({"kandidat": "zero_shot", "einstellung": "Hypothesen V1",
                     **macro_f1_ci(labels, zs.predict(texts))})  # fmt: skip
    OUT.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(rows).write_csv(OUT / "auswahl_cv.csv")
    best_c = max((r for r in rows if r["kandidat"] == "tfidf_logreg"),
                 key=lambda r: r["macro_f1"])["einstellung"]  # fmt: skip
    (OUT / "auswahl.json").write_text(json.dumps({"tfidf_logreg": best_c}, indent=2))
    print(pl.DataFrame(rows).select("kandidat", "einstellung", "macro_f1", "ci_low", "ci_high"))


def test() -> None:
    """Jeder Kandidat genau einmal auf der Testmenge (Sperre: results/classify/testlaeufe.json)."""
    tr_x, tr_y = load_labeled("train")
    te_x, te_y = load_labeled("test")
    choice = json.loads((OUT / "auswahl.json").read_text())
    best_c = float(choice["tfidf_logreg"].split("=")[1])
    lock = HoldoutLock(OUT / "testlaeufe.json")
    rows, conf = [], {}
    names = ["tfidf_logreg"] + ([] if os.environ.get("SOV_SKIP_SLOW") == "1"
                                else ["setfit", "zero_shot"])  # fmt: skip
    for name in names:
        model = candidates(best_c)[name]().fit(tr_x, tr_y)
        lock.claim(name, note=f"Trainingsfragen: {len(tr_x)}")
        pred = model.predict(te_x)
        rows.append({"kandidat": name, **macro_f1_ci(te_y, pred), "params": json.dumps(
            getattr(model, "params", {}), ensure_ascii=False)})  # fmt: skip
        conf[name] = confusion(te_y, pred)
    res = pl.DataFrame(rows).sort("macro_f1", descending=True)
    res.write_csv(OUT / "vergleich.csv")
    (OUT / "konfusion.json").write_text(json.dumps(conf, indent=2))
    best = res.row(0, named=True)
    ok = best["macro_f1"] >= config.MACRO_F1_MIN
    print(res.select("kandidat", "macro_f1", "ci_low", "ci_high", "accuracy"))
    print(f"Gewinner: {best['kandidat']} (Macro-F1 {best['macro_f1']:.2f}) – "
          f"{'Kriterium erfüllt' if ok else 'Kriterium 0,70 NICHT erfüllt'}")  # fmt: skip


def apply() -> None:
    res = pl.read_csv(OUT / "vergleich.csv").sort("macro_f1", descending=True)
    best = res.row(0, named=True)
    tr_x, tr_y = load_labeled("train")
    te_x, te_y = load_labeled("test")
    choice = json.loads((OUT / "auswahl.json").read_text())
    best_c = float(choice["tfidf_logreg"].split("=")[1])
    # Endmodell: auf allen 600 kodierten Fragen trainieren (Test ist abgeschlossen)
    model = candidates(best_c)[best["kandidat"]]().fit(tr_x + te_x, tr_y + te_y)
    df = pl.read_parquet(APPLY)
    pred = model.predict(df["text"].to_list())
    out = df.select("question_id", "year").with_columns(
        label=pl.Series(pred), verfahren=pl.lit(best["kandidat"])
    )
    out.write_parquet(config.PROCESSED_DIR / "classified_sample.parquet")
    shares = (
        out.group_by("year", "label")
        .len()
        .with_columns(n_year=pl.col("len").sum().over("year"))
        .with_columns(share=pl.col("len") / pl.col("n_year"))
    )
    z = 1.96  # Wilson-Intervall
    shares = shares.with_columns(
        ci_low=(pl.col("share") + z**2 / (2 * pl.col("n_year")) - z * (
            (pl.col("share") * (1 - pl.col("share")) + z**2 / (4 * pl.col("n_year")))
            / pl.col("n_year")).sqrt()) / (1 + z**2 / pl.col("n_year")),
        ci_high=(pl.col("share") + z**2 / (2 * pl.col("n_year")) + z * (
            (pl.col("share") * (1 - pl.col("share")) + z**2 / (4 * pl.col("n_year")))
            / pl.col("n_year")).sqrt()) / (1 + z**2 / pl.col("n_year")),
    ).sort("year", "label")  # fmt: skip
    shares.write_csv(config.PROCESSED_DIR / "text_group_shares.csv")
    card = {"datum": datetime.now().isoformat(timespec="seconds"), "verfahren": best["kandidat"],
            "test_macro_f1": best["macro_f1"], "params": best["params"],
            "trainiert_auf": len(tr_x) + len(te_x), "angewendet_auf": df.height,
            "pakete": pkg_versions(), "hypothesen": HYPOTHESES_V1}  # fmt: skip
    (OUT / "modell.json").write_text(json.dumps(card, indent=2, ensure_ascii=False))
    print(f"Angewendet: {df.height} Fragen mit {best['kandidat']}.")


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    {"prepare": prepare, "benchmark": benchmark, "select": select, "test": test,
     "apply": apply}[step]()  # fmt: skip
    _ = np  # für spätere Erweiterungen (Korrektur der Anteile)
