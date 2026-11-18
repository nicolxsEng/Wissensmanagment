"""AP07: Gruppenvergleich Grundlagen gegen Umgebung über Tags (plan.md 5.3 K7, 5.4, AP07).

- Gruppenanteil = Anteil der Fragen eines Jahres mit mindestens einem Tag der Gruppe (Nenner: alle
  Fragen der Population). Index = Anteil / Anteil im Basisjahr × 100.
- Abstand = Index Umgebung − Index Grundlagen (Effektmaß, plan.md 5.4).
- Permutationstest: zufällige, nicht überlappende Gruppen gleicher Größe aus denselben Kandidaten-
  Tags. Damit das in Sekunden läuft, werden die Fragen je Jahr auf ihre Kombination von
  Kandidaten-Tags verdichtet (mit Anzahl) und als dünn besetzte Matrix Kombination × Tag
  gespeichert; eine Frage zählt einmal, auch wenn sie mehrere Tags der Gruppe trägt.
"""

from collections.abc import Mapping, Sequence

import numpy as np
import polars as pl
from scipy import sparse

from sov import config


def has_any(tags: Sequence[str]) -> pl.Expr:
    return pl.col("tags").list.eval(pl.element().is_in(list(tags))).list.any()


def group_shares(
    q: pl.DataFrame,
    groups: Mapping[str, Sequence[str]],
    base_year: int = config.BASE_YEAR,
    exclusive: bool = False,
) -> pl.DataFrame:
    """Anteil und Index je Gruppe und Jahr. Spalten: year, gruppe, n_group, n_total, share, index.

    exclusive=True (Gegenprobe „nur eine Gruppe“, D07): Fragen mit Tags mehrerer Gruppen zählen
    in keiner Gruppe; der Nenner bleibt gleich.
    """
    flags = {g: has_any(t).alias(f"_in_{g}") for g, t in groups.items()}
    df = q.select("year", *flags.values())
    if exclusive:
        n_hit = pl.sum_horizontal([pl.col(f"_in_{g}").cast(pl.Int8) for g in groups])
        df = df.with_columns([(pl.col(f"_in_{g}") & (n_hit == 1)).alias(f"_in_{g}")
                              for g in groups])  # fmt: skip
    agg = df.group_by("year").agg(
        *[pl.col(f"_in_{g}").sum().alias(g) for g in groups], n_total=pl.len()
    )
    long = agg.unpivot(index=["year", "n_total"], variable_name="gruppe", value_name="n_group")
    long = long.with_columns(share=pl.col("n_group") / pl.col("n_total"))
    base = long.filter(pl.col("year") == base_year).select("gruppe", base_share="share")
    return (
        long.join(base, on="gruppe")
        .with_columns(index=pl.col("share") / pl.col("base_share") * 100)
        .select("year", "gruppe", pl.col("n_group").cast(pl.Int64), "n_total", "share", "index")
        .sort("gruppe", "year")
    )


def distance(shares: pl.DataFrame, year: int, a: str = "U", b: str = "G") -> float:
    """Index a − Index b in einem Jahr."""
    idx = dict(
        zip(
            *shares.filter(pl.col("year") == year).select("gruppe", "index").to_dict().values(),
            strict=True,
        )
    )
    return float(idx[a] - idx[b])


class TagMatrix:
    """Fragen je Jahr, verdichtet auf Kombinationen der Kandidaten-Tags (für schnelle Gruppen)."""

    def __init__(self, q: pl.DataFrame, tags: Sequence[str], years: Sequence[int]):
        self.tags = list(tags)
        self.years = sorted(set(years))
        pos = {t: i for i, t in enumerate(self.tags)}
        sub = q.filter(pl.col("year").is_in(self.years))
        self.n_total = np.array(
            [sub.filter(pl.col("year") == y).height for y in self.years], dtype=float
        )
        combos = (
            sub.select(
                "year",
                key=pl.col("tags")
                .list.eval(pl.element().filter(pl.element().is_in(self.tags)))
                .list.unique()
                .list.sort(),
            )
            .filter(pl.col("key").list.len() > 0)
            .group_by("year", "key")
            .len()
        )
        rows, cols = [], []
        for r, key in enumerate(combos["key"].to_list()):
            rows += [r] * len(key)
            cols += [pos[t] for t in key]
        self.m = sparse.csr_matrix(
            (np.ones(len(rows), dtype=np.float32), (rows, cols)),
            shape=(combos.height, len(self.tags)),
        )
        yi = {y: i for i, y in enumerate(self.years)}
        self.y = sparse.csr_matrix(
            (
                combos["len"].to_numpy().astype(np.float64),
                ([yi[y] for y in combos["year"].to_list()], np.arange(combos.height)),
            ),
            shape=(len(self.years), combos.height),
        )

    def indicator(self, groups: Sequence[Sequence[str]]) -> np.ndarray:
        """Matrix Tag × Gruppe mit 1, wenn der Tag zur Gruppe gehört."""
        pos = {t: i for i, t in enumerate(self.tags)}
        s = np.zeros((len(self.tags), len(groups)), dtype=np.float32)
        for j, g in enumerate(groups):
            s[[pos[t] for t in g], j] = 1
        return s

    def shares(self, s: np.ndarray, batch: int = 250) -> np.ndarray:
        """Anteile je Jahr (Zeilen) und Gruppe (Spalten von s)."""
        out = np.empty((len(self.years), s.shape[1]))
        for a in range(0, s.shape[1], batch):
            hit = (self.m @ s[:, a : a + batch]) > 0
            out[:, a : a + batch] = self.y @ hit.astype(np.float64)
        return out / self.n_total[:, None]

    def year_pos(self, year: int) -> int:
        return self.years.index(year)


def random_group_shares(
    tm: TagMatrix, n_g: int, n_u: int, n_perm: int = config.N_PERMUTATIONS, seed: int = config.SEED
) -> tuple[np.ndarray, np.ndarray]:
    """Anteile zufälliger, nicht überlappender Gruppen der Größen n_g und n_u.

    Rückgabe: (Anteile G, Anteile U), je Matrix Jahr × Permutation.
    """
    rng = np.random.default_rng(seed)
    n = len(tm.tags)
    s_g = np.zeros((n, n_perm), dtype=np.float32)
    s_u = np.zeros((n, n_perm), dtype=np.float32)
    for k in range(n_perm):
        p = rng.permutation(n)
        s_g[p[:n_g], k] = 1
        s_u[p[n_g : n_g + n_u], k] = 1
    return tm.shares(s_g), tm.shares(s_u)


def index_distance(
    tm: TagMatrix, sh_g: np.ndarray, sh_u: np.ndarray, year: int, base_year: int
) -> np.ndarray:
    """Abstand Index U − Index G je Spalte."""
    b, y = tm.year_pos(base_year), tm.year_pos(year)
    return 100 * (sh_u[y] / sh_u[b] - sh_g[y] / sh_g[b])


def permutation_summary(observed: float, random: np.ndarray) -> dict:
    """Einseitig: Anteil der Zufallsabstände ≥ beobachtet, p = (k + 1) / (N + 1)."""
    random = random[np.isfinite(random)]
    k = int((random >= observed).sum())
    return {
        "beobachtet": observed,
        "n_perm": len(random),
        "k_ge": k,
        "p": (k + 1) / (len(random) + 1),
        "perzentil": float((random < observed).mean() * 100),
        "median_zufall": float(np.median(random)),
        "q95_zufall": float(np.quantile(random, 0.95)),
        "max_zufall": float(random.max()),
    }


def leave_one_out(
    tm: TagMatrix, g: Sequence[str], u: Sequence[str], year: int, base_year: int
) -> pl.DataFrame:
    """Abstand im Vergleichsjahr ohne jeweils einen Tag."""
    variants_g = [[t for t in g if t != x] for x in g]
    variants_u = [[t for t in u if t != x] for x in u]
    full = tm.shares(tm.indicator([g, u]))
    sg = tm.shares(tm.indicator(variants_g))
    su = tm.shares(tm.indicator(variants_u))
    b, y = tm.year_pos(base_year), tm.year_pos(year)

    def idx(col):
        return 100 * col[y] / col[b]

    rows = [
        {"gruppe": "G", "ohne_tag": x, "abstand": float(idx(full[:, 1]) - idx(sg[:, i]))}
        for i, x in enumerate(g)
    ]
    rows += [
        {"gruppe": "U", "ohne_tag": x, "abstand": float(idx(su[:, i]) - idx(full[:, 0]))}
        for i, x in enumerate(u)
    ]
    return pl.DataFrame(rows)


def tag_shift(
    q: pl.DataFrame,
    tags: Sequence[str],
    years: Sequence[int] = (2019, config.BASE_YEAR, config.MAIN_POST_YEAR),
) -> pl.DataFrame:
    """Je Tag: Fragen und Anteil je Jahr, Behaltensquote (2024/2022) und Vortrend (2022/2019)."""
    y0, base, post = years
    sub = q.filter(pl.col("year").is_in(list(years)))
    totals = dict(sub.group_by("year").len().iter_rows())
    counts = (
        sub.select("year", tag=pl.col("tags").list.unique())
        .explode("tag")
        .filter(pl.col("tag").is_in(list(tags)))
        .group_by("tag", "year")
        .len()
        .pivot(on="year", index="tag", values="len")
    )
    out = pl.DataFrame({"tag": list(tags)}).join(counts, on="tag", how="left").fill_null(0)
    shares = {y: pl.col(str(y)) / totals[y] for y in years}
    return out.select(
        "tag",
        *[pl.col(str(y)).cast(pl.Int64).alias(f"n_{y}") for y in years],
        behalten=shares[post] / shares[base],
        vortrend=shares[base] / shares[y0],
    ).sort("tag")
