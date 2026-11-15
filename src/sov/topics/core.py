"""AP11: Themenanalyse der Fragetitel – gemeinsame Bausteine für BERTopic und NMF.

Nur lokale Modelle (D10). BERTopic wird erst in `run_bertopic` importiert, damit der Rest
(und die Tests) ohne PyTorch läuft.
"""

import numpy as np
import polars as pl
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from sov import config

# Wörter inkl. Programmier-Schreibweisen: c++, c#, node.js, python3, asp.net-core
TOKEN_PATTERN = r"(?u)[A-Za-z][A-Za-z0-9_+#.\-]*[A-Za-z0-9+#]|[A-Za-z]"
N_KEYWORDS = 10


def balanced_titles(
    q: pl.DataFrame, years: list[int], per_year: int, seed: int = config.SEED
) -> pl.DataFrame:
    """Gleich viele klassische Titel je Jahr (Exposé 5.3), reproduzierbar."""
    parts = []
    for y in years:
        sub = q.filter(pl.col("is_classic") & (pl.col("year") == y)).sort("question_id")
        parts.append(sub.sample(per_year, seed=seed + y, shuffle=True))
    return pl.concat(parts).select("question_id", "year", "title")


def vectorizer_kwargs() -> dict:
    return {
        "stop_words": "english",
        "token_pattern": TOKEN_PATTERN,
        "lowercase": True,
        "ngram_range": (1, 2),
        "min_df": 2,
    }


def run_nmf(titles: list[str], k: int, seed: int = config.SEED) -> tuple[np.ndarray, list]:
    """NMF auf TF-IDF der Titel. Rückgabe: Thema je Titel (−1 = kein Wort im Vokabular),
    Schlüsselwörter je Thema. Zusätzlich `run_nmf.last_scores` = Gewicht des Themas."""
    vec = TfidfVectorizer(sublinear_tf=True, **vectorizer_kwargs())
    x = vec.fit_transform(titles)
    model = NMF(n_components=k, init="nndsvda", random_state=seed, max_iter=1000)
    w = model.fit_transform(x)
    labels = np.where(w.sum(axis=1) > 0, w.argmax(axis=1), -1)
    vocab = np.array(vec.get_feature_names_out())
    keywords = [list(vocab[np.argsort(-row)[:N_KEYWORDS]]) for row in model.components_]
    run_nmf.last_scores = w.max(axis=1)
    return labels, keywords


def run_bertopic(
    titles: list[str],
    embeddings: np.ndarray,
    min_cluster_size: int,
    nr_topics: int | None,
    seed: int = config.SEED,
    embedding_model=None,
):
    """BERTopic mit festen Zufallszahlen. Ausreißer (−1) werden danach über die Embeddings dem
    ähnlichsten Thema zugeordnet (D19). Rückgabe: Labels, Schlüsselwörter, Modell, roher
    Ausreißeranteil."""
    from bertopic import BERTopic  # noqa: PLC0415
    from bertopic.representation import KeyBERTInspired  # noqa: PLC0415
    from hdbscan import HDBSCAN  # noqa: PLC0415
    from umap import UMAP  # noqa: PLC0415

    umap_model = UMAP(
        n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=seed
    )
    hdb = HDBSCAN(
        min_cluster_size=min_cluster_size, metric="euclidean", cluster_selection_method="eom",
        prediction_data=True,
    )  # fmt: skip
    model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdb,
        vectorizer_model=CountVectorizer(**vectorizer_kwargs()),
        representation_model=KeyBERTInspired(),
        nr_topics=nr_topics,
        top_n_words=N_KEYWORDS,
        calculate_probabilities=False,
        verbose=False,
    )
    topics, _ = model.fit_transform(titles, embeddings)
    raw_outlier_share = float(np.mean(np.asarray(topics) == -1))
    if raw_outlier_share > 0:
        topics = model.reduce_outliers(titles, topics, strategy="embeddings",
                                       embeddings=embeddings)  # fmt: skip
        model.update_topics(titles, topics=topics, vectorizer_model=CountVectorizer(
            **vectorizer_kwargs()), representation_model=KeyBERTInspired())  # fmt: skip
    labels = np.asarray(topics)
    ids = sorted(t for t in set(labels.tolist()) if t != -1)
    keywords = {t: [w for w, _ in model.get_topic(t)][:N_KEYWORDS] for t in ids}
    return labels, keywords, model, raw_outlier_share


def centroid_scores(embeddings: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Kosinus-Ähnlichkeit jedes Titels zum Mittelpunkt seines Themas."""
    e = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    scores = np.zeros(len(labels))
    for t in set(labels.tolist()):
        idx = labels == t
        c = e[idx].mean(axis=0)
        scores[idx] = e[idx] @ (c / np.linalg.norm(c))
    return scores


def typical_and_check_titles(
    titles: list[str],
    labels: np.ndarray,
    score: np.ndarray,
    n_typical: int = 5,
    n_check: int = config.TOPIC_CHECK_TITLES,
    seed: int = config.SEED,
) -> dict[int, dict]:
    """Je Thema: typische Titel (höchste Zugehörigkeit, zum Benennen) und davon getrennte
    Zufallstitel zum Prüfen (plan.md Abschnitt 9)."""
    rng = np.random.default_rng(seed)
    out = {}
    for t in sorted(set(labels.tolist()) - {-1}):
        idx = np.flatnonzero(labels == t)
        order = idx[np.argsort(-score[idx], kind="stable")]
        typical = order[:n_typical]
        rest = order[n_typical:]
        check = rng.choice(rest, size=min(n_check, len(rest)), replace=False) if len(rest) else []
        out[t] = {
            "size": int(len(idx)),
            "typical": [titles[i] for i in typical],
            "check": [titles[i] for i in check],
        }
    return out


def topic_diversity(keyword_lists: list[list[str]]) -> float:
    """Anteil verschiedener Wörter unter allen Schlüsselwörtern (1 = keine Überschneidung)."""
    words = [w for kws in keyword_lists for w in kws]
    return len(set(words)) / len(words) if words else float("nan")


def evaluate_checks(
    checks: pl.DataFrame, min_fit: int = config.TOPIC_CHECK_MIN_FIT
) -> pl.DataFrame:
    """checks: code, passt_A, passt_B ('j'/'n'). Bestanden, wenn beide >= min_fit von 10."""
    yes = lambda c: (pl.col(c).str.to_lowercase().str.strip_chars() == "j").sum()  # noqa: E731
    return (
        checks.group_by("code")
        .agg(n=pl.len(), passt_A=yes("passt_A"), passt_B=yes("passt_B"))
        .with_columns(bestanden=(pl.col("passt_A") >= min_fit) & (pl.col("passt_B") >= min_fit))
        .sort("code")
    )
