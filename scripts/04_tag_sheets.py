"""AP04: Kodierbögen für die blinde Einordnung der Tags.

uv run python scripts/04_tag_sheets.py

Erzeugt in coding/tags/:
  tags_kodierer_A.csv, tags_kodierer_B.csv  alle Kandidaten-Tags, je eigene Zufallsreihenfolge
  uebung_10.csv                              10 Übungstags, die NICHT zu den Kandidaten gehören
  kalibrierung_30.csv                        30 weitere Nicht-Kandidaten für die Kalibrierung der
                                             Modelle (AP16, D25), ohne Überschneidung mit uebung_10
Bögen mit Einträgen werden nie überschrieben.
"""

import polars as pl

from sov import config
from sov.coding import build_tag_sheet, write_sheet
from sov.io import load_questions
from sov.se_client import fetch_wikis

OUT = config.CODING_DIR / "tags"


def practice_tags(n: int = 10, seed: int = config.SEED + 3, exclude=()) -> list[str]:
    """Zufällige Tags knapp unter der Schwelle (100–149 Fragen 2022), also keine Kandidaten."""
    q = load_questions(["year", "tags", "is_classic"])
    counts = (
        q.filter(pl.col("is_classic") & (pl.col("year") == config.BASE_YEAR))
        .select(pl.col("tags").alias("tag"))
        .explode("tag")
        .group_by("tag")
        .agg(n=pl.len())
        .filter(pl.col("n").is_between(100, config.MIN_TAG_COUNT - 1))
        .filter(~pl.col("tag").is_in(list(exclude)))
        .sort("tag")
    )
    return counts.sample(n, seed=seed)["tag"].sort().to_list()


def main() -> None:
    wiki = pl.read_csv(config.PROCESSED_DIR / "tag_wiki.csv")
    assert wiki.height == config.N_TAGS_EXPECTED, wiki.height
    for name, seed in (("A", config.SEED + 1), ("B", config.SEED + 2)):
        path = OUT / f"tags_kodierer_{name}.csv"
        write_sheet(build_tag_sheet(wiki, seed), path)
        print(f"Bogen {name}: {path} ({wiki.height} Tags)")

    cand = set(wiki["tag"])
    ptags = [t for t in practice_tags() if t not in cand]
    pwiki = fetch_wikis(ptags, cache_name="tag_wikis_uebung")
    path = OUT / "uebung_10.csv"
    write_sheet(build_tag_sheet(pwiki, config.SEED + 4), path)
    print(f"Übungsbogen: {path} ({len(ptags)} Tags)")

    ktags = [t for t in practice_tags(30, config.SEED + 5, exclude=ptags) if t not in cand]
    kwiki = fetch_wikis(ktags, cache_name="tag_wikis_kalibrierung")
    path = OUT / "kalibrierung_30.csv"
    write_sheet(build_tag_sheet(kwiki, config.SEED + 6), path)
    print(f"Kalibrierungsbogen: {path} ({len(ktags)} Tags)")


if __name__ == "__main__":
    main()
