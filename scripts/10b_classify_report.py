"""AP10, Nachbereitung: korrigierte Anteile (adjusted classify and count), Modellkarte, Bericht.

uv run python scripts/10b_classify_report.py      # nach `10_classify.py apply`

Liest nur Ergebnisse (vergleich.csv, konfusion.json, modell.json, text_group_shares.csv) und
berührt die Testmenge nicht. Ausgaben: data/processed/text_group_shares_adjusted.csv,
results/classify/modell.md, results/classify/bericht.md
"""

import json
from datetime import datetime

import numpy as np
import polars as pl

from sov import config
from sov.classify.evaluate import LABELS

OUT = config.RESULTS_DIR / "classify"


def misclassification(conf: list[list[int]]) -> np.ndarray:
    """M[j, i] = P(Vorhersage j | wahr i) aus der Konfusionsmatrix (Zeilen wahr, Spalten Vorh.)."""
    c = np.asarray(conf, dtype=float)
    return (c / c.sum(axis=1, keepdims=True)).T


def adjust(observed: np.ndarray, m: np.ndarray) -> np.ndarray:
    """Löst M · π = beobachtet (kleinste Quadrate), auf [0, 1] begrenzt und normiert."""
    pi, *_ = np.linalg.lstsq(m, observed, rcond=None)
    pi = np.clip(pi, 0, 1)
    return pi / pi.sum()


def de(x: float, d: int = 1, sign: bool = False) -> str:
    s = f"{x:+,.{d}f}" if sign else f"{x:,.{d}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def main() -> None:
    res = pl.read_csv(OUT / "vergleich.csv").sort("macro_f1", descending=True)
    conf = json.loads((OUT / "konfusion.json").read_text())
    card = json.loads((OUT / "modell.json").read_text())
    best = card["verfahren"]
    m = misclassification(conf[best])
    shares = pl.read_csv(config.PROCESSED_DIR / "text_group_shares.csv")
    rows = []
    for y in sorted(shares["year"].unique().to_list()):
        s = shares.filter(pl.col("year") == y)
        obs = np.array([s.filter(pl.col("label") == lab)["share"].sum() for lab in LABELS])
        adj = adjust(obs, m)
        rows += [{"year": y, "label": lab, "share": float(o), "share_adjusted": float(a)}
                 for lab, o, a in zip(LABELS, obs, adj, strict=True)]  # fmt: skip
    adj_df = pl.DataFrame(rows)
    adj_df.write_csv(config.PROCESSED_DIR / "text_group_shares_adjusted.csv")

    # Modellkarte
    card_lines = [
        "# Modellkarte AP10",
        "",
        f"- Datum: {card['datum']}",
        f"- Verfahren: {best}",
        f"- Macro-F1 auf der Testmenge: {de(card['test_macro_f1'], 2)}",
        f"- Einstellungen: `{card['params']}`",
        f"- Endmodell trainiert auf {card['trainiert_auf']} Konsensfragen (Training + Test), "
        f"angewendet auf {card['angewendet_auf']} Fragen",
        f"- Pakete: `{json.dumps(card['pakete'], ensure_ascii=False)}`",
        f"- Zero-Shot-Modell: {config.ZERO_SHOT_MODEL}; SetFit-Basis: {config.SETFIT_BASE_MODEL}",
        "- Hypothesensätze (Zero-Shot): "
        + "; ".join(f"{k}: {v}" for k, v in card["hypothesen"].items()),
        "- Alle Modelle lokal; keine Cloud-API.",
    ]
    (OUT / "modell.md").write_text("\n".join(card_lines) + "\n", encoding="utf-8")

    # Bericht
    c = np.asarray(conf[best])
    gu = c[:2, :2]
    f1_gu = []
    for i in range(2):
        tp, fp, fn = gu[i, i], gu[:, i].sum() - gu[i, i], gu[i, :].sum() - gu[i, i]
        f1_gu.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
    lines = [
        "# Automatische Einordnung der Fragetexte (AP10)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Referenz: Fragen, die beide Sprachmodelle "
        "gleich einordneten (AP09); Training 335, Test 121 (je Kandidat genau einmal, D06).",
        "",
        "## Vergleich auf der Testmenge",
        "",
        "| Kandidat | Macro-F1 [95-%-KI] | Genauigkeit | F1 G | F1 U | F1 S |",
        "|---|---|---|---|---|---|",
    ]
    for r in res.to_dicts():
        lines.append(
            f"| {r['kandidat']} | {de(r['macro_f1'], 2)} [{de(r['ci_low'], 2)}; "
            f"{de(r['ci_high'], 2)}] | {de(100 * r['accuracy'], 0)} % | {de(r['f1_G'], 2)} | "
            f"{de(r['f1_U'], 2)} | {de(r['f1_S'], 2)} |"
        )
    ok = res.row(0, named=True)["macro_f1"] >= config.MACRO_F1_MIN
    lines += [
        "",
        f"Gewinner: **{best}**; Kriterium Macro-F1 ≥ {de(config.MACRO_F1_MIN, 2)}: "
        f"{'erfüllt' if ok else 'NICHT erfüllt (Textanalyse nur als Hinweis deuten, Plan AP10)'}.",
        f"Nur G und U (ohne die {int(c[2].sum())} S-Testfragen): Macro-F1 "
        f"{de(float(np.mean(f1_gu)), 2)}.",
        "",
        "Konfusionsmatrix des Gewinners (Zeilen wahr, Spalten vorhergesagt):",
        "",
        "| | " + " | ".join(LABELS) + " |",
        "|---|" + "---|" * len(LABELS),
    ]
    for lab, row in zip(LABELS, c.tolist(), strict=True):
        lines.append(f"| {lab} | " + " | ".join(str(v) for v in row) + " |")
    lines += [
        "",
        "## Anteile je Jahr (roh und korrigiert)",
        "",
        "Korrektur: adjusted classify and count mit der Konfusionsmatrix des Gewinners. Bei S "
        "beruht sie auf sehr wenigen Testfragen und ist entsprechend unsicher.",
        "",
        "| Jahr | G roh | G korr. | U roh | U korr. | S roh | S korr. |",
        "|---|---|---|---|---|---|---|",
    ]
    for y in sorted(adj_df["year"].unique().to_list()):
        d = {r["label"]: r for r in adj_df.filter(pl.col("year") == y).to_dicts()}
        lines.append(
            f"| {y} | "
            + " | ".join(
                f"{de(100 * d[lab]['share'])} % | {de(100 * d[lab]['share_adjusted'])} %"
                for lab in LABELS
            )
            + " |"
        )
    (OUT / "bericht.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
