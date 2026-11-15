"""AP03: Kandidaten-Tags, Tag-Wikis, Synonyme und Brüche.

uv run python scripts/03_tag_audit.py

Ausgaben (data/processed/): tags_candidates.csv, tag_wiki.csv, tag_synonyms.csv,
tag_breaks.csv; Protokoll results/logs/tag_audit.md.
ACHTUNG: tags_candidates.csv, tag_breaks.csv und das Protokoll enthalten Fragezahlen je Tag.
Erst nach der Tag-Kodierung (AP05) öffnen. tag_wiki.csv enthält keine Zahlen.
"""

from datetime import datetime

import polars as pl

from sov import config
from sov.io import load_questions
from sov.se_client import fetch_synonyms, fetch_wikis
from sov.tags import candidate_tags, canonicalize, detect_breaks, synonym_map, tag_year_counts

WARN = (
    "> **Nicht vor Abschluss der Tag-Kodierung (AP05) öffnen.** Diese Datei enthält "
    "Fragezahlen und Entwicklungen einzelner Tags und würde die blinde Einordnung verletzen."
)


def successors(q: pl.DataFrame, year: int, exclude: str, k: int = 3) -> list[str]:
    """Tags, die im Jahr des Abbruchs aus dem Nichts auftauchen (Hinweis auf Nachfolger)."""
    sub = (
        q.filter(pl.col("is_classic") & pl.col("year").is_in([year - 1, year]))
        .select("year", pl.col("tags").alias("tag"))
        .explode("tag")
        .group_by("tag", "year")
        .agg(n=pl.len())
        .pivot(on="year", index="tag", values="n")
        .fill_null(0)
    )
    prev, cur = str(year - 1), str(year)
    if prev not in sub.columns or cur not in sub.columns:
        return []
    hits = sub.filter((pl.col(prev) < 5) & (pl.col(cur) >= 20) & (pl.col("tag") != exclude))
    return hits.sort(cur, descending=True)["tag"].head(k).to_list()


def recommendation(kind: str, year: int, is_syn_source: bool, succ: list[str]) -> str:
    if kind == "entsteht":
        return "behalten (Index 2022 = 100 unproblematisch; im Trendzeitraum anfangs ~0)"
    if is_syn_source:
        return "ist heute Synonym eines anderen Tags → mit Ziel-Tag zusammenlegen"
    if succ:
        return f"Nachfolger prüfen ({', '.join(succ)}) → zusammenlegen oder ausschließen"
    if year > config.BASE_YEAR:
        return "auf stackoverflow.com prüfen: Tag geändert/gesperrt oder echter Einbruch?"
    return "auf stackoverflow.com prüfen (Umbenennung/Abschaffung) → ausschließen, falls ja"


def main() -> None:
    q_raw = load_questions(["year", "tags", "is_classic"], canonical_tags=False)
    out = config.PROCESSED_DIR
    out.mkdir(parents=True, exist_ok=True)

    # 1) Kandidaten mit rohen Tags (wie im Exposé: 272)
    raw_cands = candidate_tags(q_raw)
    raw_tags = raw_cands["tag"].to_list()
    raw_cands.rename({"n": "n_2022"}).write_csv(out / "tags_candidates_raw.csv")

    # 2) Synonyme der Kandidaten und der KI-Tags holen
    print("Hole Tag-Wikis und Synonyme von der Stack Exchange API …")
    syn = fetch_synonyms(sorted(set(raw_tags) | config.AI_TAGS))
    # Kommt ein Synonym (from_tag) in unseren Daten noch als eigener Tag vor?
    all_tags = (
        q_raw.filter(pl.col("is_classic")).select(pl.col("tags").alias("tag")).explode("tag")
        .group_by("tag").agg(n_in_daten=pl.len())
    )  # fmt: skip
    syn = syn.join(all_tags, left_on="from_tag", right_on="tag", how="left").with_columns(
        pl.col("n_in_daten").fill_null(0)
    )
    syn.write_csv(out / "tag_synonyms.csv")
    syn_sources = set(syn.filter(pl.col("n_in_daten") > 0)["from_tag"].to_list())

    # 3) Synonyme zusammenführen (D15) und Kandidaten neu bestimmen
    q = canonicalize(q_raw, synonym_map(syn))
    cands = candidate_tags(q)
    tags = cands["tag"].to_list()
    cands.rename({"n": "n_2022"}).write_csv(out / "tags_candidates.csv")
    merged = sorted(set(raw_tags) - set(tags))
    print(f"Kandidaten: {len(raw_tags)} roh, {len(tags)} nach Zusammenführen der Synonyme")

    wiki = fetch_wikis(raw_tags).filter(pl.col("tag").is_in(tags))
    wiki.write_csv(out / "tag_wiki.csv")

    counts = tag_year_counts(q, tags)
    totals = q.filter(pl.col("is_classic")).group_by("year").agg(n_year=pl.len())
    breaks = detect_breaks(counts, totals)
    # Gegenprobe: Brüche ohne Zusammenführen (sollten die zusammengeführten Tags sein)
    raw_breaks = detect_breaks(tag_year_counts(q_raw, raw_tags), totals)
    raw_breaks.write_csv(out / "tag_breaks_raw.csv")

    # Brüche anreichern
    c = counts.join(totals.with_columns(pl.col("year").cast(pl.Int64)), on="year")
    rows = []
    for b in breaks.to_dicts():
        t, y = b["tag"], b["year"]
        ser = {r["year"]: r["n"] for r in c.filter(pl.col("tag") == t).to_dicts()}
        succ = successors(q, y, t) if b["kind"] == "abbruch" else []
        rows.append(
            b
            | {
                "n_vorjahr": ser.get(y - 1, 0),
                "n_jahr": ser.get(y, 0),
                "n_2022": ser.get(config.BASE_YEAR, 0),
                "nachfolger_hinweis": ", ".join(succ),
                "empfehlung": recommendation(b["kind"], y, t in syn_sources, succ),
            }
        )
    br = pl.DataFrame(rows) if rows else breaks
    br.write_csv(out / "tag_breaks.csv")

    no_wiki = wiki.filter(pl.col("wiki_auszug") == "")["tag"].to_list()
    n_abbruch = br.filter(pl.col("kind") == "abbruch").height if rows else 0
    n_neu = br.filter(pl.col("kind") == "entsteht").height if rows else 0
    lines = [
        "# Tag-Prüfung (AP03)",
        "",
        WARN,
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}",
        "",
        "## Zusammenfassung",
        "",
        f"- Kandidaten (≥ {config.MIN_TAG_COUNT} klassische Fragen im Oktober "
        f"{config.BASE_YEAR}): {len(raw_tags)} mit rohen Tags "
        f"(Exposé: {config.N_TAGS_EXPECTED_RAW}), "
        f"**{len(tags)}** nach Zusammenführen der Synonyme (D15)",
        f"- Zusammengeführt, weil selbst Synonym eines anderen Kandidaten: "
        f"{', '.join(f'`{m}`' for m in merged) or 'keine'}",
        f"- Abbrüche ohne Zusammenführen: {raw_breaks.filter(pl.col('kind') == 'abbruch').height}, "
        f"mit Zusammenführen: siehe unten",
        f"- Tag-Wiki vorhanden: {len(tags) - len(no_wiki)}, ohne Wiki: {len(no_wiki)}"
        + (f" ({', '.join(no_wiki)})" if no_wiki else ""),
        f"- Synonyme mit einem Kandidaten oder KI-Tag als Ziel: {syn.height}; davon kommen "
        f"{len(syn_sources)} in den Daten noch als eigener Tag vor",
        f"- Brüche: {n_abbruch} Abbrüche, {n_neu} Tags entstehen nach {config.TREND_START}",
        "",
        "## Erkennungsregeln",
        "",
        "- **Abbruch:** In einem Jahr hat der Tag weniger als 10 % der Fragen, die bei gleichem "
        "Anteil wie im Vorjahr zu erwarten wären (mindestens 10 erwartet). Der allgemeine "
        "Rückgang ist so herausgerechnet.",
        f"- **Entsteht:** erstes Jahr mit ≥ 10 Fragen liegt nach {config.TREND_START}.",
        "- **Nachfolger-Hinweis:** Tags mit < 5 Fragen im Vorjahr und ≥ 20 im Jahr des Abbruchs.",
        "",
        "## Brüche",
        "",
        "| Tag | Art | Jahr | Vorjahr | Jahr | 2022 | Nachfolger-Hinweis | Empfehlung | "
        "Entscheidung Team |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in br.sort("kind", "year", "tag").to_dicts() if rows else []:
        lines.append(
            f"| `{r['tag']}` | {r['kind']} | {r['year']} | {r['n_vorjahr']} | {r['n_jahr']} | "
            f"{r['n_2022']} | {r['nachfolger_hinweis']} | {r['empfehlung']} | |"
        )
    lines += ["", "## Synonyme, die in den Daten noch als eigener Tag vorkommen", ""]
    hits = syn.filter(pl.col("n_in_daten") > 0)
    if hits.height:
        lines += ["| Synonym | Ziel | Fragen in den Daten | angelegt |", "|---|---|---|---|"]
        for r in hits.to_dicts():
            lines.append(
                f"| `{r['from_tag']}` | `{r['to_tag']}` | {r['n_in_daten']} | {r['created']} |"
            )
    else:
        lines.append("Keine. Alte Fragen wurden beim Zusammenlegen offenbar umgetaggt.")
    # Wie viele Fragen tragen ein altes Synonym? (Begründung für D15)
    src = syn["from_tag"].to_list()
    imp = (
        q_raw.filter(pl.col("is_classic")).group_by("year")
        .agg(share=pl.col("tags").list.eval(pl.element().is_in(src)).list.any().mean() * 100)
        .sort("year")
    )  # fmt: skip
    n_canon = len(tags)
    lines += [
        "",
        "## Synonyme verzerren Tag-Zeitreihen am ChatGPT-Schnitt",
        "",
        "Anteil klassischer Fragen mit mindestens einem alten Synonym-Tag (in %):",
        "",
        "| " + " | ".join(str(y) for y in imp["year"]) + " |",
        "|" + "---|" * imp.height,
        "| " + " | ".join(f"{v:.2f}".replace(".", ",") for v in imp["share"]) + " |",
        "",
        "Neue Fragen werden automatisch auf den Haupt-Tag abgebildet, ältere behalten das "
        "Synonym. Ohne Zusammenführen sinken Synonym-Tags ab 2023 künstlich und Haupt-Tags "
        "steigen künstlich, genau am Schnitt. **Vorschlag D15:** vor jeder Tag-Auswertung alle "
        "Synonyme auf ihren Haupt-Tag abbilden (`sov.tags.canonicalize`). Dann gibt es "
        f"**{n_canon}** statt {len(raw_tags)} Kandidaten-Tags, weil "
        f"{len(raw_tags) - n_canon} Kandidaten selbst Synonyme anderer Kandidaten sind. "
        "**Entschieden am 15.11.2026: angenommen.**",
    ]
    lines += [
        "",
        "Entscheidungen bitte in `docs/entscheidungen.md` eintragen (offener Punkt "
        "„Umgang mit Tag-Brüchen“), danach in AP07 berücksichtigen.",
    ]
    log = config.RESULTS_DIR / "logs" / "tag_audit.md"
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"Fertig: {len(tags)} Kandidaten, {len(no_wiki)} ohne Wiki, {syn.height} Synonyme, "
        f"{n_abbruch} Abbrüche, {n_neu} neu entstanden. Protokoll: {log}"
    )


if __name__ == "__main__":
    main()
