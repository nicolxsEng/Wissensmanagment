"""AP11: Themenanalyse der Fragetitel – Probelauf BERTopic gegen NMF.

uv sync --group topics            # einmalig (PyTorch, BERTopic)
uv run python scripts/11_topics.py pilot          # beide Verfahren, Benennungsbogen
uv run python scripts/11_topics.py pilot-checks   # nach dem Benennen: Prüfbögen A/B
uv run python scripts/11_topics.py pilot-eval     # nach der Prüfung: Bewertung, Wahl
uv run python scripts/11_topics.py main BERTopic  # Hauptlauf (D28: beide Verfahren, erst BERTopic)
uv run python scripts/11_topics.py main NMF       # gleiche Themenzahl wie BERTopic
uv run python scripts/11_topics.py main-eval      # nach Benennen/Prüfen: Vergleich, Gewinner

Benennen und Prüfen übernehmen die Sprachmodelle: scripts/16_llm_coding.py themen-namen/-check.
"""

import hashlib
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
PRE_YEARS = (config.TREND_START, config.BASE_YEAR)  # Mittel 2015–2022 gegen 2023–2026


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


def fit_bertopic(texts: list[str], e: np.ndarray, mcs: int = 10):
    """BERTopic; Themenzahl in den Bereich config.TOPIC_N_RANGE bringen (wie im Probelauf)."""
    lo, hi = config.TOPIC_N_RANGE
    nr = None
    for _ in range(4):
        labels, kws, _model, outl = run_bertopic(
            texts, e, min_cluster_size=mcs, nr_topics=nr, embedding_model=embedding_model()
        )
        k = len(kws)
        if k > hi:
            nr = (lo + hi) // 2 + 1  # +1: BERTopic zählt das Ausreißer-Thema mit
        elif k < lo and mcs > 4:
            mcs -= 3
        else:
            break
    return labels, kws, outl, mcs, nr


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
    lab_a, kw_a, outl, mcs, nr = fit_bertopic(texts, e)
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


def read_checks(set_name: str = "probelauf") -> tuple[pl.DataFrame, str]:
    """Prüfurteile: die zwei Sprachmodelle (AP16), sonst die Bögen der Autor:innen (A/B)."""
    llm = [TOPIC_DIR / f"llm_themen_check_{set_name}_{k}.csv" for k in config.LLM_CODERS]
    if all(f.exists() for f in llm):
        files, who = llm, " und ".join(config.LLM_MODELS[k] for k in config.LLM_CODERS)
    else:
        files, who = [TOPIC_DIR / f"themen_check_{c}.csv" for c in "AB"], "Autor:innen A und B"
    a, b = (pl.read_csv(f, separator=";", infer_schema=False) for f in files)
    j = a.select("code", "titel", pl.col("passt").alias("passt_A")).join(
        b.select("code", "titel", pl.col("passt").alias("passt_B")), on=["code", "titel"]
    )
    return j, who


def pilot_eval() -> None:
    j, who = read_checks("probelauf")
    names_file = TOPIC_DIR / "llm_themen_namen_probelauf.csv"
    names = (
        pl.read_csv(names_file, separator=";", infer_schema=False)
        if names_file.exists()
        else pl.read_csv(NAME_SHEET, separator=";", infer_schema=False)
    ).select("code", "name")
    ev = (
        evaluate_checks(j)
        .join(pl.read_csv(MAPPING).select("code", "method"), on="code")
        .join(names, on="code", how="left")
    )
    fit = (pl.col("passt_A") + pl.col("passt_B")) / (2 * pl.col("n"))
    summary = ev.group_by("method").agg(
        themen=pl.len(), bestanden=pl.col("bestanden").sum(),
        anteil=pl.col("bestanden").mean(), passung=fit.mean(),
        unklar=(pl.col("name").str.to_lowercase() == "unclear").sum(),
    ).sort("anteil", descending=True)  # fmt: skip
    best = summary.row(0, named=True)
    tie = summary.height > 1 and summary["anteil"][0] == summary["anteil"][1]
    lines = [
        "# Probelauf – Bewertung der Themen",
        "",
        "| Verfahren | Themen | bestanden | Anteil | mittlere Passung | „unclear“ |",
        "|---|---|---|---|---|---|",
    ]
    for r in summary.to_dicts():
        lines.append(f"| {r['method']} | {r['themen']} | {r['bestanden']} | {r['anteil']:.0%} | "
                     f"{r['passung']:.0%} | {r['unklar']} |")  # fmt: skip
    verdict = (
        "**Gleichstand** beim Anteil bestandener Themen – Wahl nicht durch das vorab "
        "festgelegte Kriterium entschieden (mittlere Passung = Anteil passender Titel, "
        "gemittelt über beide Modelle, nur zur Information)."
        if tie
        else f"**Gewählt: {best['method']}** (höherer Anteil bestandener Themen). "
        "Bitte in docs/entscheidungen.md eintragen."
    )
    lines += ["", verdict, "",
              f"Geprüft von: {who}. Bestanden, wenn beide ≥ {config.TOPIC_CHECK_MIN_FIT} von "
              f"{config.TOPIC_CHECK_TITLES} Titeln als passend einstufen.", "",
              "| Code | Verfahren | Name | passt A | passt B | Titel | bestanden |",
              "|---|---|---|---|---|---|---|"]  # fmt: skip
    for r in ev.sort(["method", "code"]).to_dicts():
        ok = "ja" if r["bestanden"] else "nein"
        lines.append(f"| {r['code']} | {r['method']} | {r['name']} | {r['passt_A']} | "
                     f"{r['passt_B']} | {r['n']} | {ok} |")  # fmt: skip
    ev.write_csv(RES / "probelauf_bewertung.csv")
    (RES / "probelauf_bewertung.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main_paths(method: str) -> dict:
    """Ausgaben des Hauptlaufs je Verfahren (D28: beide Verfahren, dann Wahl)."""
    m = method.lower()
    return {
        "set": f"haupt-{m}",
        "topics": config.PROCESSED_DIR / f"topics_{m}.parquet",
        "mapping": config.PROCESSED_DIR / f"topics_mapping_{m}.csv",
        "checks": config.PROCESSED_DIR / f"topics_checktitles_{m}.parquet",
        "sheet": TOPIC_DIR / f"themen_benennen_{m}.csv",
        "card": RES / f"modell_{m}.json",
    }


def main_run() -> None:
    """Hauptlauf auf allen ausgewogenen Titeln; erst BERTopic, dann NMF mit gleicher Themenzahl."""
    method = sys.argv[2] if len(sys.argv) > 2 else ""
    if method not in ("BERTopic", "NMF"):
        raise SystemExit("Verfahren angeben: main BERTopic | main NMF")
    paths = main_paths(method)
    t0 = time.perf_counter()
    titles, emb = titles_and_embeddings()
    texts = titles["title"].to_list()
    info: dict = {"verfahren": method}
    if method == "BERTopic":
        labels, kws, outl, mcs, nr = fit_bertopic(texts, emb)
        score = centroid_scores(emb, labels)
        info |= {"min_cluster_size": mcs, "nr_topics": nr, "ausreisser_roh": round(outl, 4)}
    else:
        bt = main_paths("BERTopic")["card"]
        if not bt.exists():
            raise SystemExit("Erst `main BERTopic`: NMF bekommt dieselbe Themenzahl (D28).")
        k = json.loads(bt.read_text())["themen"]
        labels, kw_list = run_nmf(texts, k=k)
        score = run_nmf.last_scores
        kws = dict(enumerate(kw_list))
        info |= {"k": k, "ohne_thema": int((labels < 0).sum())}
    sel = typical_and_check_titles(texts, labels, score, seed=config.SEED + 41)
    ids = sorted(sel)
    code_of = {t: f"T{i:02d}" for i, t in enumerate(ids, start=1)}
    df = titles.with_columns(topic_id=pl.Series(labels.tolist())).with_columns(
        code=pl.col("topic_id").replace_strict(code_of, default=None, return_dtype=pl.String)
    )
    df.select("question_id", "year", "topic_id", "code").write_parquet(paths["topics"])
    rows, checks, sheet = [], [], []
    for t, code in code_of.items():
        s = sel[t]
        sub = df.filter(pl.col("topic_id") == t)
        qid = dict(zip(sub["title"], sub["question_id"], strict=False))
        rows.append({"code": code, "topic_id": t, "size": s["size"],
                     "keywords": ", ".join(kws[t]),
                     "typisch_ids": ",".join(str(qid[x]) for x in s["typical"])})  # fmt: skip
        checks += [{"code": code, "titel": x} for x in s["check"]]
        typ = s["typical"] + [""] * (5 - len(s["typical"]))
        sheet.append({"code": code, "schluesselwoerter": ", ".join(kws[t]),
                      **{f"typisch_{i + 1}": typ[i] for i in range(5)}, "name": None})  # fmt: skip
    pl.DataFrame(rows).write_csv(paths["mapping"])
    pl.DataFrame(checks).write_parquet(paths["checks"])
    write_sheet(pl.DataFrame(sheet, schema_overrides={"name": pl.String}), paths["sheet"],
                entry_cols=("name",))  # fmt: skip
    digest = hashlib.sha256(labels.astype(np.int64).tobytes()).hexdigest()[:12]
    same = None
    if paths["card"].exists():
        old = json.loads(paths["card"].read_text())
        if old.get("titel") == len(texts):
            same = old.get("labels_hash") == digest
    card = {
        "datum": datetime.now().isoformat(timespec="seconds"),
        "titel": len(texts),
        "titel_je_jahr": titles.group_by("year").len().sort("year")["len"].to_list(),
        "themen": len(ids),
        "seed": config.SEED,
        "labels_hash": digest,
        "wie_vorheriger_lauf": same,
        "embedding_modell": config.EMBEDDING_MODEL,
        "embedding_revision": model_revision(config.EMBEDDING_MODEL),
        **info,
        "pakete": {p: version(p) for p in ("bertopic", "sentence-transformers", "umap-learn",
                                           "hdbscan", "scikit-learn", "torch")},
        "laufzeit_s": round(time.perf_counter() - t0, 1),
    }  # fmt: skip
    RES.mkdir(parents=True, exist_ok=True)
    paths["card"].write_text(json.dumps(card, indent=2, ensure_ascii=False))
    print(json.dumps(card, indent=2, ensure_ascii=False))
    print(f"Benennungsbogen: {paths['sheet']}")


def _pct(x: float) -> str:
    return f"{100 * x:.1f}".replace(".", ",") + " %"


def evaluate_method(method: str) -> tuple[pl.DataFrame, pl.DataFrame, str]:
    """Prüfergebnis und Anteile vor/nach je Thema für ein Verfahren des Hauptlaufs."""
    paths = main_paths(method)
    j, who = read_checks(paths["set"])
    names = pl.read_csv(TOPIC_DIR / f"llm_themen_namen_{paths['set']}.csv", separator=";",
                        infer_schema=False).select("code", "name")  # fmt: skip
    mapping = pl.read_csv(paths["mapping"], infer_schema_length=0).with_columns(
        pl.col("size").cast(pl.Int64)
    )
    topics = pl.read_parquet(paths["topics"])
    n_year = topics.group_by("year").len("n_year")
    shares = (
        topics.filter(pl.col("code").is_not_null())
        .group_by("year", "code").len("n")
        .join(n_year, on="year")
        .with_columns(share=pl.col("n") / pl.col("n_year"))
        .join(names, on="code")
        .sort("code", "year")
    )  # fmt: skip
    pre = pl.col("year").is_between(*PRE_YEARS)
    change = (
        shares.group_by("code")
        .agg(vorher=pl.col("share").filter(pre).mean(), nachher=pl.col("share").filter(~pre).mean())
        .with_columns(diff=pl.col("nachher") - pl.col("vorher"))
    )  # fmt: skip
    tab = (
        mapping.join(names, on="code").join(evaluate_checks(j), on="code", how="left")
        .join(change, on="code")
        .with_columns(passung=(pl.col("passt_A") + pl.col("passt_B")) / (2 * pl.col("n")),
                      bestanden=pl.col("bestanden").fill_null(False))
        .sort("diff", descending=True)
    )  # fmt: skip
    return tab, shares, who


def topic_table(tab: pl.DataFrame) -> list[str]:
    titles = pl.read_parquet(config.PROCESSED_DIR / "topic_titles.parquet")
    title_of = dict(zip(titles["question_id"], titles["title"], strict=True))
    lines = [
        "| Code | Name | Schlüsselwörter | Beispiel | vorher | nachher | Δ (Pp.) | passt A/B "
        "| bestanden |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in tab.to_dicts():
        qid = int(r["typisch_ids"].split(",")[0])
        ex = title_of.get(qid, "").replace("|", "/")[:70]
        ok = "ja" if r["bestanden"] else "nein"
        d = f"{100 * r['diff']:+.1f}".replace(".", ",")
        name = r["name"] if r["bestanden"] else f"{r['name']} (nicht bestätigt)"
        lines.append(
            f"| {r['code']} | {name} | {', '.join(r['keywords'].split(', ')[:5])} | "
            f"[{ex}](https://stackoverflow.com/q/{qid}) | {_pct(r['vorher'])} | "
            f"{_pct(r['nachher'])} | {d} | {r['passt_A']}/{r['passt_B']} | {ok} |"
        )
    return lines


def main_eval() -> None:
    """Beide Verfahren bewerten, Gewinner nach D28, Themenliste des Gewinners."""
    res = {m: evaluate_method(m) for m in ("BERTopic", "NMF")}
    summ = pl.DataFrame([
        {"verfahren": m, "themen": tab.height, "bestanden": int(tab["bestanden"].sum()),
         "anteil": float(tab["bestanden"].mean()), "passung": float(tab["passung"].mean()),
         "unklar": tab.filter(pl.col("name").str.to_lowercase() == "unclear").height}
        for m, (tab, _s, _w) in res.items()
    ]).sort(["anteil", "passung"], descending=True)  # fmt: skip
    best = summ.row(0, named=True)
    tie = summ["anteil"][0] == summ["anteil"][1]
    method = best["verfahren"]
    tab, shares, who = res[method]
    ok = best["anteil"] >= 0.8
    for m, (t_m, _s, _w) in res.items():
        t_m.write_csv(RES / f"themen_{m.lower()}.csv")
    shares.write_csv(config.PROCESSED_DIR / "topic_shares.csv")
    pl.read_parquet(main_paths(method)["topics"]).write_parquet(
        config.PROCESSED_DIR / "topics.parquet"
    )
    lines = [
        "# Themen der Fragetitel (AP11)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Namen: {config.LLM_MODELS['qwen']}; "
        f"geprüft von {who} (je Thema 10 Zufallstitel; bestanden, wenn beide ≥ "
        f"{config.TOPIC_CHECK_MIN_FIT}/10). Auswahl nach D28.",
        "",
        "## Vergleich der Verfahren im Hauptlauf",
        "",
        "| Verfahren | Themen | bestanden | Anteil | mittlere Passung | „unclear“ |",
        "|---|---|---|---|---|---|",
    ]
    for r in summ.to_dicts():
        lines.append(f"| {r['verfahren']} | {r['themen']} | {r['bestanden']} | "
                     f"{r['anteil']:.0%} | {r['passung']:.0%} | {r['unklar']} |")  # fmt: skip
    lines += [
        "",
        f"**Gewinner: {method}**"
        + (" (Gleichstand beim Anteil, entschieden über die mittlere Passung, D28)" if tie else "")
        + ". Kriterium ≥ 80 % bestandene Themen: "
        + ("erfüllt." if ok else "**nicht erfüllt** – Themenanalyse nur als Hinweis (D28)."),
        "",
        f"## Themen ({method}), sortiert nach Veränderung",
        "",
        f"Anteile: Mittel {PRE_YEARS[0]}–{PRE_YEARS[1]} gegen {PRE_YEARS[1] + 1}–"
        f"{max(config.TOPIC_YEARS)}. Inhaltlich gedeutet werden nur bestandene Themen.",
        "",
        *topic_table(tab),
    ]
    (RES / "themen.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "pilot"
    steps = {"pilot": pilot, "pilot-checks": pilot_checks, "pilot-eval": pilot_eval,
             "main": main_run, "main-eval": main_eval}  # fmt: skip
    steps[step]()
