"""AP11: Themenanalyse der Fragetitel – Probelauf BERTopic gegen NMF.

uv sync --group topics            # einmalig (PyTorch, BERTopic)
uv run python scripts/11_topics.py pilot          # beide Verfahren, Benennungsbogen
uv run python scripts/11_topics.py pilot-checks   # nach dem Benennen: Prüfbögen A/B
uv run python scripts/11_topics.py pilot-eval     # nach der Prüfung: Bewertung, Wahl

Der Hauptlauf auf allen Titeln folgt, wenn das Verfahren gewählt ist.
"""

import json
import sys
import time
from datetime import datetime
from importlib.metadata import version

import numpy as np
import polars as pl

from sov import config
from sov.coding import write_sheet
from sov.io import load_questions
from sov.topics.core import (
    balanced_titles,
    centroid_scores,
    evaluate_checks,
    run_bertopic,
    run_nmf,
    topic_diversity,
    typical_and_check_titles,
)

TOPIC_DIR = config.CODING_DIR / "topics"
RES = config.RESULTS_DIR / "topics"
EMB_DIR = config.INTERIM_DIR / "topics"
PILOT_PER_YEAR = 84  # 12 × 84 = 1.008 ≈ 1.000 Titel (plan.md AP11)
NAME_SHEET = TOPIC_DIR / "themen_benennen_probelauf.csv"
MAPPING = config.PROCESSED_DIR / "topics_pilot_mapping.csv"  # Code -> Verfahren (verdeckt)
CHECK_TITLES = config.PROCESSED_DIR / "topics_pilot_checktitles.parquet"


def model_revision(name: str) -> str:
    try:
        from huggingface_hub import HfApi  # noqa: PLC0415

        return HfApi().model_info(name).sha or "unbekannt"
    except Exception as e:  # noqa: BLE001
        return f"unbekannt ({type(e).__name__})"


def embedding_model():
    """Lokales Satz-Embedding-Modell (einmal geladen, danach aus dem Zwischenspeicher)."""
    if not hasattr(embedding_model, "_m"):
        import torch  # noqa: PLC0415
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        embedding_model._m = SentenceTransformer(config.EMBEDDING_MODEL, device=device)
    return embedding_model._m


def titles_and_embeddings() -> tuple[pl.DataFrame, np.ndarray]:
    """Gleich viele Titel je Oktober 2015–2026 (so viele wie 2026) und ihre Embeddings."""
    q = load_questions(["question_id", "year", "is_classic", "title"], canonical_tags=False)
    per_year = q.filter(pl.col("is_classic") & (pl.col("year") == 2026)).height
    titles = balanced_titles(q, config.TOPIC_YEARS, per_year)
    titles.write_parquet(config.PROCESSED_DIR / "topic_titles.parquet")
    EMB_DIR.mkdir(parents=True, exist_ok=True)
    emb_path = EMB_DIR / f"emb_{config.EMBEDDING_MODEL.split('/')[-1]}.npy"
    ids_path = emb_path.with_suffix(".ids.json")
    ids = titles["question_id"].to_list()
    if emb_path.exists() and json.loads(ids_path.read_text()) == ids:
        return titles, np.load(emb_path)
    emb = embedding_model().encode(titles["title"].to_list(), batch_size=128,
                                   show_progress_bar=True)  # fmt: skip
    np.save(emb_path, emb)
    ids_path.write_text(json.dumps(ids))
    return titles, emb


def pilot() -> None:
    t0 = time.perf_counter()
    titles, emb = titles_and_embeddings()
    pilot_df = pl.concat(
        [
            titles.filter(pl.col("year") == y).sample(PILOT_PER_YEAR, seed=config.SEED + 7 + y)
            for y in config.TOPIC_YEARS
        ]
    )
    idx = np.array(
        [titles["question_id"].to_list().index(i) for i in pilot_df["question_id"].to_list()]
    )
    texts, e = pilot_df["title"].to_list(), emb[idx]

    # A: BERTopic (Themenzahl in den Bereich 20–40 bringen)
    ta = time.perf_counter()
    lo, hi = config.TOPIC_N_RANGE
    mcs, nr = 10, None
    for _ in range(4):
        lab_a, kw_a, _model, outl = run_bertopic(
            texts, e, min_cluster_size=mcs, nr_topics=nr, embedding_model=embedding_model()
        )
        k = len(kw_a)
        if k > hi:
            nr = (lo + hi) // 2 + 1  # +1: BERTopic zählt das Ausreißer-Thema mit
        elif k < lo and mcs > 4:
            mcs -= 3
        else:
            break
    ta = time.perf_counter() - ta
    score_a = centroid_scores(e, lab_a)

    # B: NMF mit derselben Themenzahl
    tb = time.perf_counter()
    lab_b, kw_b_list = run_nmf(texts, k=len(kw_a))
    score_b = run_nmf.last_scores
    tb = time.perf_counter() - tb
    kw_b = dict(enumerate(kw_b_list))

    sel_a = typical_and_check_titles(texts, lab_a, score_a, seed=config.SEED + 21)
    sel_b = typical_and_check_titles(texts, lab_b, score_b, seed=config.SEED + 22)
    topics = [("BERTopic", t, kw_a[t], s) for t, s in sel_a.items()] + [
        ("NMF", t, kw_b[t], s) for t, s in sel_b.items()
    ]
    order = np.random.default_rng(config.SEED + 23).permutation(len(topics))
    rows, checks = [], []
    for code_i, j in enumerate(order, start=1):
        method, t, kws, s = topics[j]
        code = f"T{code_i:02d}"
        rows.append({"code": code, "method": method, "topic_id": t, "size": s["size"],
                     "keywords": ", ".join(kws)})  # fmt: skip
        checks += [{"code": code, "titel": x} for x in s["check"]]
    mapping = pl.DataFrame(rows)
    mapping.write_csv(MAPPING)
    pl.DataFrame(checks).write_parquet(CHECK_TITLES)

    sheet = []
    for r in mapping.sort("code").to_dicts():
        s = (sel_a if r["method"] == "BERTopic" else sel_b)[r["topic_id"]]
        typ = s["typical"] + [""] * (5 - len(s["typical"]))
        sheet.append({"code": r["code"], "schluesselwoerter": r["keywords"],
                      **{f"typisch_{i + 1}": typ[i] for i in range(5)}, "name": None})  # fmt: skip
    TOPIC_DIR.mkdir(parents=True, exist_ok=True)
    write_sheet(
        pl.DataFrame(sheet, schema_overrides={"name": pl.String}), NAME_SHEET, entry_cols=("name",)
    )

    # Kennzahlen und Modellkarte
    RES.mkdir(parents=True, exist_ok=True)

    def stats(labels, kws):
        sizes = np.bincount(labels[labels >= 0])
        sizes = sizes[sizes > 0]
        return (len(sizes), int(sizes.min()), int(np.median(sizes)), int(sizes.max()),
                topic_diversity(list(kws.values())))  # fmt: skip

    sa, sb = stats(lab_a, kw_a), stats(lab_b, kw_b)
    rev = model_revision(config.EMBEDDING_MODEL)
    md = [
        "# Themenanalyse – Probelauf (AP11)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. {len(texts)} Titel "
        f"({PILOT_PER_YEAR} je Oktober 2015–2026), klassische Fragen.",
        "",
        "| Kennzahl | A: BERTopic | B: NMF |",
        "|---|---|---|",
        f"| Themen | {sa[0]} | {sb[0]} |",
        f"| Titel je Thema (min / Median / max) | {sa[1]} / {sa[2]} / {sa[3]} | "
        f"{sb[1]} / {sb[2]} / {sb[3]} |",
        f"| Vielfalt der Schlüsselwörter (1 = keine Doppelung) | {sa[4]:.2f} | {sb[4]:.2f} |",
        f"| Ausreißer vor Zuordnung | {outl:.0%} | – |",
        f"| Laufzeit | {ta:.0f} s | {tb:.1f} s |",
        "",
        "Entscheidend ist die menschliche Prüfung (≥ 8 von 10 passenden Titeln, beide "
        "unabhängig). Die Themen beider Verfahren sind im Benennungsbogen gemischt und "
        "neutral kodiert; `data/processed/topics_pilot_mapping.csv` erst nach der Prüfung öffnen.",
    ]
    (RES / "probelauf.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    card = {
        "datum": datetime.now().isoformat(timespec="seconds"),
        "titel": len(texts),
        "seed": config.SEED,
        "embedding_modell": config.EMBEDDING_MODEL,
        "embedding_revision": rev,
        "bertopic": {
            "min_cluster_size": mcs,
            "nr_topics": nr,
            "umap": "n_neighbors=15, n_components=5, min_dist=0, cosine",
            "hdbscan": "eom",
            "ausreisser": "reduce_outliers(strategy='embeddings')",
            "darstellung": "KeyBERTInspired",
        },  # fmt: skip
        "nmf": {
            "k": len(kw_a),
            "tfidf": "sublinear, englische Stoppwörter, 1–2-Gramme, min_df=2",
            "init": "nndsvda",
        },  # fmt: skip
        "pakete": {
            p: version(p)
            for p in (
                "bertopic",
                "sentence-transformers",
                "umap-learn",
                "hdbscan",
                "scikit-learn",
                "torch",
            )
        },  # fmt: skip
    }
    (RES / "modell_probelauf.json").write_text(json.dumps(card, indent=2, ensure_ascii=False))
    print(f"Fertig in {time.perf_counter() - t0:.0f} s: BERTopic {sa[0]} Themen, NMF {sb[0]} "
          f"Themen. Benennungsbogen: {NAME_SHEET}")  # fmt: skip


def pilot_checks() -> None:
    names = pl.read_csv(NAME_SHEET, separator=";", infer_schema=False)
    missing = names.filter(pl.col("name").fill_null("").str.strip_chars() == "")["code"].to_list()
    if missing:
        raise SystemExit(f"Noch ohne Namen: {', '.join(missing)} – erst benennen.")
    checks = pl.read_parquet(CHECK_TITLES).join(names.select("code", "name"), on="code")
    for coder, seed in (("A", config.SEED + 31), ("B", config.SEED + 32)):
        rng = np.random.default_rng(seed)
        codes = list(rng.permutation(checks["code"].unique().sort().to_list()))
        parts = [checks.filter(pl.col("code") == c).sample(fraction=1.0, shuffle=True,
                                                           seed=seed) for c in codes]  # fmt: skip
        sheet = (
            pl.concat(parts)
            .with_columns(nr=pl.int_range(1, checks.height + 1), passt=pl.lit(None, pl.String))
            .select("nr", "code", "name", "titel", "passt")
        )
        write_sheet(sheet, TOPIC_DIR / f"themen_check_{coder}.csv", entry_cols=("passt",))
    print(f"Prüfbögen erzeugt: {TOPIC_DIR}/themen_check_A.csv, themen_check_B.csv")


def pilot_eval() -> None:
    a = pl.read_csv(TOPIC_DIR / "themen_check_A.csv", separator=";", infer_schema=False)
    b = pl.read_csv(TOPIC_DIR / "themen_check_B.csv", separator=";", infer_schema=False)
    j = a.select("code", "titel", pl.col("passt").alias("passt_A")).join(
        b.select("code", "titel", pl.col("passt").alias("passt_B")), on=["code", "titel"]
    )
    ev = evaluate_checks(j).join(pl.read_csv(MAPPING).select("code", "method"), on="code")
    summary = ev.group_by("method").agg(
        themen=pl.len(), bestanden=pl.col("bestanden").sum(),
        anteil=pl.col("bestanden").mean(),
    ).sort("anteil", descending=True)  # fmt: skip
    best = summary.row(0, named=True)
    lines = [
        "# Probelauf – Bewertung der Themen",
        "",
        "| Verfahren | Themen | bestanden | Anteil |",
        "|---|---|---|---|",
    ]
    for r in summary.to_dicts():
        lines.append(f"| {r['method']} | {r['themen']} | {r['bestanden']} | {r['anteil']:.0%} |")
    lines += ["", f"**Gewählt: {best['method']}** (höherer Anteil bestandener Themen). "
              "Bitte in docs/entscheidungen.md eintragen."]  # fmt: skip
    ev.write_csv(RES / "probelauf_bewertung.csv")
    (RES / "probelauf_bewertung.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "pilot"
    {"pilot": pilot, "pilot-checks": pilot_checks, "pilot-eval": pilot_eval}[step]()
